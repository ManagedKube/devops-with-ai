"""
VPC component for AWS infrastructure.

This module creates a complete VPC infrastructure including:
- VPC with configurable CIDR block
- 3 public subnets in different availability zones
- 3 private subnets in different availability zones
- Internet Gateway for public subnet internet access
- Route tables with appropriate routes
- Default security group allowing all traffic
- Optional NAT Gateways for private subnet internet access
"""
from typing import Optional, TypedDict
import pulumi
from pulumi import ResourceOptions, Output
from pulumi_aws import ec2


class VpcArgs(TypedDict, total=False):
    """Arguments for creating a VPC with public and private subnets.

    Required fields:
        vpcCidr: CIDR block for the VPC (e.g., "10.0.0.0/16").
        publicSubnetCidrs: List of 3 CIDR blocks for public subnets.
        privateSubnetCidrs: List of 3 CIDR blocks for private subnets.
        availabilityZones: List of 3 availability zones to use.
        tagsAdditional: Additional tags to apply to all resources.

    Optional fields:
        enableNatGateway: Whether to create NAT Gateways in private subnets.
            Default: False.
        vpcName: Name for the VPC. If not provided, uses resource name.
    """

    vpcCidr: pulumi.Input[str]
    publicSubnetCidrs: pulumi.Input[list[pulumi.Input[str]]]
    privateSubnetCidrs: pulumi.Input[list[pulumi.Input[str]]]
    availabilityZones: pulumi.Input[list[pulumi.Input[str]]]
    tagsAdditional: pulumi.Input[dict[str, pulumi.Input[str]]]
    enableNatGateway: Optional[pulumi.Input[bool]]
    vpcName: Optional[pulumi.Input[str]]


class Vpc(pulumi.ComponentResource):
    """Creates a complete VPC infrastructure with public and private subnets.

    This component creates:
        - A VPC with the specified CIDR block
        - 3 public subnets across availability zones
        - 3 private subnets across availability zones
        - An Internet Gateway for public internet access
        - Route tables with appropriate routes
        - A default security group allowing all traffic
        - Optional NAT Gateways for private subnet internet access
    """

    vpc_id: pulumi.Output[str]
    vpc_arn: pulumi.Output[str]
    public_subnet_ids: pulumi.Output[list[str]]
    private_subnet_ids: pulumi.Output[list[str]]
    internet_gateway_id: pulumi.Output[str]
    nat_gateway_ids: pulumi.Output[list[str]]
    default_security_group_id: pulumi.Output[str]

    def __init__(
        self,
        name: str,
        args: VpcArgs,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        """Initialize the VPC component.

        Args:
            name: The unique name for this component instance.
            args: Configuration arguments for the VPC.
            opts: Optional Pulumi resource options.
        """
        super().__init__('vpc:index:Vpc', name, {}, opts)

        # Helper to read snake_case or camelCase keys
        def pick(d: dict, snake: str, camel: str, default=None):
            """Get value from dict supporting both snake_case and camelCase."""
            return d.get(snake, d.get(camel, default))

        # Get required parameters
        vpc_cidr = pick(args, "vpc_cidr", "vpcCidr")
        public_subnet_cidrs = pick(args, "public_subnet_cidrs", "publicSubnetCidrs")
        private_subnet_cidrs = pick(args, "private_subnet_cidrs", "privateSubnetCidrs")
        availability_zones = pick(args, "availability_zones", "availabilityZones")
        tags_additional = pick(args, "tags_additional", "tagsAdditional") or {}

        # Get optional parameters with defaults
        enable_nat_gateway = pick(args, "enable_nat_gateway", "enableNatGateway", False)
        vpc_name = pick(args, "vpc_name", "vpcName", name)

        # Create VPC
        vpc_tags = {
            "Name": vpc_name,
            **tags_additional,
        }

        vpc = ec2.Vpc(
            f"{name}-vpc",
            cidr_block=vpc_cidr,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            tags=vpc_tags,
            opts=ResourceOptions(parent=self),
        )

        # Create Internet Gateway
        igw_tags = {
            "Name": f"{vpc_name}-igw",
            **tags_additional,
        }

        internet_gateway = ec2.InternetGateway(
            f"{name}-igw",
            vpc_id=vpc.id,
            tags=igw_tags,
            opts=ResourceOptions(parent=self),
        )

        # Create public subnets
        public_subnets = []
        for i in range(3):
            subnet_tags = {
                "Name": f"{vpc_name}-public-subnet-{i+1}",
                "Type": "public",
                **tags_additional,
            }

            # Get the availability zone from the list
            def get_az(zones, idx):
                """Extract availability zone at index from list."""
                if isinstance(zones, list):
                    return zones[idx] if idx < len(zones) else zones[0]
                return zones

            # Get CIDR block from the list
            def get_cidr(cidrs, idx):
                """Extract CIDR block at index from list."""
                if isinstance(cidrs, list):
                    return cidrs[idx] if idx < len(cidrs) else cidrs[0]
                return cidrs

            subnet = ec2.Subnet(
                f"{name}-public-subnet-{i+1}",
                vpc_id=vpc.id,
                cidr_block=Output.from_input(public_subnet_cidrs).apply(
                    lambda cidrs: get_cidr(cidrs, i)
                ),
                availability_zone=Output.from_input(availability_zones).apply(
                    lambda zones: get_az(zones, i)
                ),
                map_public_ip_on_launch=True,
                tags=subnet_tags,
                opts=ResourceOptions(parent=self),
            )
            public_subnets.append(subnet)

        # Create public route table
        public_rt_tags = {
            "Name": f"{vpc_name}-public-rt",
            **tags_additional,
        }

        public_route_table = ec2.RouteTable(
            f"{name}-public-rt",
            vpc_id=vpc.id,
            tags=public_rt_tags,
            opts=ResourceOptions(parent=self),
        )

        # Create route to Internet Gateway for public route table
        ec2.Route(
            f"{name}-public-route",
            route_table_id=public_route_table.id,
            destination_cidr_block="0.0.0.0/0",
            gateway_id=internet_gateway.id,
            opts=ResourceOptions(parent=self),
        )

        # Associate public subnets with public route table
        for i, subnet in enumerate(public_subnets):
            ec2.RouteTableAssociation(
                f"{name}-public-rta-{i+1}",
                subnet_id=subnet.id,
                route_table_id=public_route_table.id,
                opts=ResourceOptions(parent=self),
            )

        # Create private subnets
        private_subnets = []
        for i in range(3):
            subnet_tags = {
                "Name": f"{vpc_name}-private-subnet-{i+1}",
                "Type": "private",
                **tags_additional,
            }

            subnet = ec2.Subnet(
                f"{name}-private-subnet-{i+1}",
                vpc_id=vpc.id,
                cidr_block=Output.from_input(private_subnet_cidrs).apply(
                    lambda cidrs: get_cidr(cidrs, i)
                ),
                availability_zone=Output.from_input(availability_zones).apply(
                    lambda zones: get_az(zones, i)
                ),
                map_public_ip_on_launch=False,
                tags=subnet_tags,
                opts=ResourceOptions(parent=self),
            )
            private_subnets.append(subnet)

        # Create NAT Gateways if enabled
        nat_gateways = []
        if enable_nat_gateway:
            for i, public_subnet in enumerate(public_subnets):
                # Allocate Elastic IP for NAT Gateway
                eip_tags = {
                    "Name": f"{vpc_name}-nat-eip-{i+1}",
                    **tags_additional,
                }

                eip = ec2.Eip(
                    f"{name}-nat-eip-{i+1}",
                    domain="vpc",
                    tags=eip_tags,
                    opts=ResourceOptions(parent=self),
                )

                # Create NAT Gateway
                nat_tags = {
                    "Name": f"{vpc_name}-nat-gw-{i+1}",
                    **tags_additional,
                }

                nat_gateway = ec2.NatGateway(
                    f"{name}-nat-gw-{i+1}",
                    subnet_id=public_subnet.id,
                    allocation_id=eip.id,
                    tags=nat_tags,
                    opts=ResourceOptions(parent=self, depends_on=[internet_gateway]),
                )
                nat_gateways.append(nat_gateway)

                # Create private route table for this AZ
                private_rt_tags = {
                    "Name": f"{vpc_name}-private-rt-{i+1}",
                    **tags_additional,
                }

                private_route_table = ec2.RouteTable(
                    f"{name}-private-rt-{i+1}",
                    vpc_id=vpc.id,
                    tags=private_rt_tags,
                    opts=ResourceOptions(parent=self),
                )

                # Create route to NAT Gateway
                ec2.Route(
                    f"{name}-private-route-{i+1}",
                    route_table_id=private_route_table.id,
                    destination_cidr_block="0.0.0.0/0",
                    nat_gateway_id=nat_gateway.id,
                    opts=ResourceOptions(parent=self),
                )

                # Associate private subnet with route table
                ec2.RouteTableAssociation(
                    f"{name}-private-rta-{i+1}",
                    subnet_id=private_subnets[i].id,
                    route_table_id=private_route_table.id,
                    opts=ResourceOptions(parent=self),
                )
        else:
            # Create a single private route table without NAT Gateway
            private_rt_tags = {
                "Name": f"{vpc_name}-private-rt",
                **tags_additional,
            }

            private_route_table = ec2.RouteTable(
                f"{name}-private-rt",
                vpc_id=vpc.id,
                tags=private_rt_tags,
                opts=ResourceOptions(parent=self),
            )

            # Associate all private subnets with this route table
            for i, subnet in enumerate(private_subnets):
                ec2.RouteTableAssociation(
                    f"{name}-private-rta-{i+1}",
                    subnet_id=subnet.id,
                    route_table_id=private_route_table.id,
                    opts=ResourceOptions(parent=self),
                )

        # Create default security group that allows all inbound and outbound traffic
        sg_tags = {
            "Name": f"{vpc_name}-default-sg",
            **tags_additional,
        }

        default_security_group = ec2.SecurityGroup(
            f"{name}-default-sg",
            vpc_id=vpc.id,
            description="Default security group allowing all inbound and outbound traffic",
            ingress=[
                ec2.SecurityGroupIngressArgs(
                    protocol="-1",
                    from_port=0,
                    to_port=0,
                    cidr_blocks=["0.0.0.0/0"],
                    description="Allow all inbound traffic",
                )
            ],
            egress=[
                ec2.SecurityGroupEgressArgs(
                    protocol="-1",
                    from_port=0,
                    to_port=0,
                    cidr_blocks=["0.0.0.0/0"],
                    description="Allow all outbound traffic",
                )
            ],
            tags=sg_tags,
            opts=ResourceOptions(parent=self),
        )

        # Set outputs
        self.vpc_id = vpc.id
        self.vpc_arn = vpc.arn
        self.public_subnet_ids = Output.all(*[s.id for s in public_subnets])
        self.private_subnet_ids = Output.all(*[s.id for s in private_subnets])
        self.internet_gateway_id = internet_gateway.id
        self.nat_gateway_ids = Output.all(*[ng.id for ng in nat_gateways]) if nat_gateways else Output.from_input([])
        self.default_security_group_id = default_security_group.id

        self.register_outputs({
            'vpc_id': self.vpc_id,
            'vpc_arn': self.vpc_arn,
            'public_subnet_ids': self.public_subnet_ids,
            'private_subnet_ids': self.private_subnet_ids,
            'internet_gateway_id': self.internet_gateway_id,
            'nat_gateway_ids': self.nat_gateway_ids,
            'default_security_group_id': self.default_security_group_id,
        })
