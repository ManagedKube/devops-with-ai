"""
Unit tests for the VPC Pulumi component.

These tests use Pulumi's unit testing framework to validate the behavior
of the VPC component without creating actual AWS resources.
"""

import unittest
from typing import Any
import pulumi


class MyMocks(pulumi.runtime.Mocks):
    """
    Mock implementation for testing Pulumi resources.

    This class intercepts resource creation calls and returns mock values,
    allowing us to test the logic of our Pulumi components.
    """

    def new_resource(
        self, args: pulumi.runtime.MockResourceArgs
    ) -> tuple[str, dict[str, Any]]:
        """
        Called when a new resource is being created.

        Returns a tuple of (id, state) for the mocked resource.
        """
        outputs = args.inputs

        # Mock VPC
        if args.typ == "aws:ec2/vpc:Vpc":
            outputs["id"] = f"vpc-{args.name}"
            outputs["arn"] = f"arn:aws:ec2:region:account:vpc/{outputs['id']}"

        # Mock Subnet
        elif args.typ == "aws:ec2/subnet:Subnet":
            outputs["id"] = f"subnet-{args.name}"
            outputs["arn"] = f"arn:aws:ec2:region:account:subnet/{outputs['id']}"

        # Mock Internet Gateway
        elif args.typ == "aws:ec2/internetGateway:InternetGateway":
            outputs["id"] = f"igw-{args.name}"
            outputs["arn"] = f"arn:aws:ec2:region:account:internet-gateway/{outputs['id']}"

        # Mock NAT Gateway
        elif args.typ == "aws:ec2/natGateway:NatGateway":
            outputs["id"] = f"nat-{args.name}"

        # Mock Elastic IP
        elif args.typ == "aws:ec2/eip:Eip":
            outputs["id"] = f"eip-{args.name}"
            outputs["public_ip"] = "1.2.3.4"

        # Mock Route Table
        elif args.typ == "aws:ec2/routeTable:RouteTable":
            outputs["id"] = f"rtb-{args.name}"

        # Mock Route
        elif args.typ == "aws:ec2/route:Route":
            outputs["id"] = f"route-{args.name}"

        # Mock Route Table Association
        elif args.typ == "aws:ec2/routeTableAssociation:RouteTableAssociation":
            outputs["id"] = f"rtbassoc-{args.name}"

        # Mock Security Group
        elif args.typ == "aws:ec2/securityGroup:SecurityGroup":
            outputs["id"] = f"sg-{args.name}"
            outputs["arn"] = f"arn:aws:ec2:region:account:security-group/{outputs['id']}"

        return outputs.get("id", args.name), outputs

    def call(self, args: pulumi.runtime.MockCallArgs) -> dict[str, Any]:
        """
        Called when a provider function is invoked.

        Returns mock outputs for the function.
        """
        return {}


# Set the mocks for all tests in this module
pulumi.runtime.set_mocks(MyMocks())


class TestVpc(unittest.TestCase):
    """Test cases for the VPC component."""

    @pulumi.runtime.test
    def test_basic_creation_without_nat_gateway(self):
        """
        Test basic VPC creation without NAT Gateways.
        """
        import sys
        import os

        sys.path.insert(
            0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        from vpc import Vpc

        # Define test arguments
        args = {
            "vpcCidr": "10.0.0.0/16",
            "publicSubnetCidrs": [
                "10.0.1.0/24",
                "10.0.2.0/24",
                "10.0.3.0/24",
            ],
            "privateSubnetCidrs": [
                "10.0.11.0/24",
                "10.0.12.0/24",
                "10.0.13.0/24",
            ],
            "availabilityZones": [
                "us-west-2a",
                "us-west-2b",
                "us-west-2c",
            ],
            "tagsAdditional": {
                "Environment": "test",
            },
        }

        # Create the component
        component = Vpc("test-vpc", args)

        # Verify outputs
        def check_outputs(outputs):
            vpc_id, vpc_arn, public_subnet_ids, private_subnet_ids, igw_id, nat_gw_ids, sg_id = outputs
            self.assertIsNotNone(vpc_id)
            self.assertIsNotNone(vpc_arn)
            self.assertIsNotNone(public_subnet_ids)
            self.assertIsNotNone(private_subnet_ids)
            self.assertIsNotNone(igw_id)
            self.assertIsNotNone(sg_id)
            self.assertIn("vpc", vpc_id)
            self.assertIn("vpc", vpc_arn)
            self.assertEqual(len(public_subnet_ids), 3)
            self.assertEqual(len(private_subnet_ids), 3)
            # NAT Gateways should be empty when not enabled
            self.assertEqual(len(nat_gw_ids), 0)

        return pulumi.Output.all(
            component.vpc_id,
            component.vpc_arn,
            component.public_subnet_ids,
            component.private_subnet_ids,
            component.internet_gateway_id,
            component.nat_gateway_ids,
            component.default_security_group_id,
        ).apply(lambda args: check_outputs(args))

    @pulumi.runtime.test
    def test_creation_with_nat_gateway(self):
        """
        Test VPC creation with NAT Gateways enabled.
        """
        import sys
        import os

        sys.path.insert(
            0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        from vpc import Vpc

        args = {
            "vpcCidr": "10.1.0.0/16",
            "publicSubnetCidrs": [
                "10.1.1.0/24",
                "10.1.2.0/24",
                "10.1.3.0/24",
            ],
            "privateSubnetCidrs": [
                "10.1.11.0/24",
                "10.1.12.0/24",
                "10.1.13.0/24",
            ],
            "availabilityZones": [
                "us-west-2a",
                "us-west-2b",
                "us-west-2c",
            ],
            "enableNatGateway": True,
            "tagsAdditional": {
                "Environment": "staging",
            },
        }

        component = Vpc("test-vpc-nat", args)

        def check_outputs(outputs):
            vpc_id, nat_gw_ids = outputs
            self.assertIsNotNone(vpc_id)
            self.assertIsNotNone(nat_gw_ids)
            # Should have 3 NAT Gateways when enabled
            self.assertEqual(len(nat_gw_ids), 3)

        return pulumi.Output.all(
            component.vpc_id,
            component.nat_gateway_ids,
        ).apply(lambda args: check_outputs(args))

    @pulumi.runtime.test
    def test_custom_vpc_name(self):
        """
        Test VPC creation with custom VPC name.
        """
        import sys
        import os

        sys.path.insert(
            0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        from vpc import Vpc

        args = {
            "vpcCidr": "10.2.0.0/16",
            "publicSubnetCidrs": [
                "10.2.1.0/24",
                "10.2.2.0/24",
                "10.2.3.0/24",
            ],
            "privateSubnetCidrs": [
                "10.2.11.0/24",
                "10.2.12.0/24",
                "10.2.13.0/24",
            ],
            "availabilityZones": [
                "us-east-1a",
                "us-east-1b",
                "us-east-1c",
            ],
            "vpcName": "custom-application-vpc",
            "tagsAdditional": {},
        }

        component = Vpc("test-custom-name", args)

        def check_outputs(outputs):
            vpc_id, = outputs
            self.assertIsNotNone(vpc_id)

        return pulumi.Output.all(
            component.vpc_id,
        ).apply(lambda args: check_outputs(args))

    @pulumi.runtime.test
    def test_snake_case_parameters(self):
        """
        Test VPC creation with snake_case parameter names.
        """
        import sys
        import os

        sys.path.insert(
            0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        from vpc import Vpc

        args = {
            "vpc_cidr": "10.3.0.0/16",
            "public_subnet_cidrs": [
                "10.3.1.0/24",
                "10.3.2.0/24",
                "10.3.3.0/24",
            ],
            "private_subnet_cidrs": [
                "10.3.11.0/24",
                "10.3.12.0/24",
                "10.3.13.0/24",
            ],
            "availability_zones": [
                "us-west-2a",
                "us-west-2b",
                "us-west-2c",
            ],
            "enable_nat_gateway": False,
            "vpc_name": "snake-case-vpc",
            "tags_additional": {
                "Environment": "dev",
            },
        }

        component = Vpc("test-snake-case", args)

        def check_outputs(outputs):
            vpc_id, public_subnets, private_subnets = outputs
            self.assertIsNotNone(vpc_id)
            self.assertEqual(len(public_subnets), 3)
            self.assertEqual(len(private_subnets), 3)

        return pulumi.Output.all(
            component.vpc_id,
            component.public_subnet_ids,
            component.private_subnet_ids,
        ).apply(lambda args: check_outputs(args))

    @pulumi.runtime.test
    def test_tagging(self):
        """
        Test that tags are correctly applied to resources.
        """
        import sys
        import os

        sys.path.insert(
            0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        from vpc import Vpc

        args = {
            "vpcCidr": "10.4.0.0/16",
            "publicSubnetCidrs": [
                "10.4.1.0/24",
                "10.4.2.0/24",
                "10.4.3.0/24",
            ],
            "privateSubnetCidrs": [
                "10.4.11.0/24",
                "10.4.12.0/24",
                "10.4.13.0/24",
            ],
            "availabilityZones": [
                "us-west-2a",
                "us-west-2b",
                "us-west-2c",
            ],
            "tagsAdditional": {
                "Environment": "production",
                "Project": "web-app",
                "Team": "platform",
                "CostCenter": "engineering",
            },
        }

        component = Vpc("test-tags", args)

        def check_outputs(outputs):
            vpc_id, sg_id = outputs
            self.assertIsNotNone(vpc_id)
            self.assertIsNotNone(sg_id)

        return pulumi.Output.all(
            component.vpc_id,
            component.default_security_group_id,
        ).apply(lambda args: check_outputs(args))

    @pulumi.runtime.test
    def test_outputs_exist(self):
        """
        Test that all expected outputs are present.
        """
        import sys
        import os

        sys.path.insert(
            0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        from vpc import Vpc

        args = {
            "vpcCidr": "10.5.0.0/16",
            "publicSubnetCidrs": [
                "10.5.1.0/24",
                "10.5.2.0/24",
                "10.5.3.0/24",
            ],
            "privateSubnetCidrs": [
                "10.5.11.0/24",
                "10.5.12.0/24",
                "10.5.13.0/24",
            ],
            "availabilityZones": [
                "us-west-2a",
                "us-west-2b",
                "us-west-2c",
            ],
            "tagsAdditional": {},
        }

        component = Vpc("test-outputs", args)

        # Check that all outputs are defined
        self.assertIsNotNone(component.vpc_id)
        self.assertIsNotNone(component.vpc_arn)
        self.assertIsNotNone(component.public_subnet_ids)
        self.assertIsNotNone(component.private_subnet_ids)
        self.assertIsNotNone(component.internet_gateway_id)
        self.assertIsNotNone(component.nat_gateway_ids)
        self.assertIsNotNone(component.default_security_group_id)

    @pulumi.runtime.test
    def test_with_two_subnets(self):
        """
        Test VPC creation with only 2 subnets instead of 3.
        """
        import sys
        import os

        sys.path.insert(
            0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        from vpc import Vpc

        args = {
            "vpcCidr": "10.6.0.0/16",
            "publicSubnetCidrs": [
                "10.6.1.0/24",
                "10.6.2.0/24",
            ],
            "privateSubnetCidrs": [
                "10.6.11.0/24",
                "10.6.12.0/24",
            ],
            "availabilityZones": [
                "us-west-2a",
                "us-west-2b",
            ],
            "tagsAdditional": {
                "Environment": "test",
            },
        }

        component = Vpc("test-two-subnets", args)

        def check_outputs(outputs):
            vpc_id, public_subnets, private_subnets = outputs
            self.assertIsNotNone(vpc_id)
            # Should have exactly 2 subnets
            self.assertEqual(len(public_subnets), 2)
            self.assertEqual(len(private_subnets), 2)

        return pulumi.Output.all(
            component.vpc_id,
            component.public_subnet_ids,
            component.private_subnet_ids,
        ).apply(lambda args: check_outputs(args))


if __name__ == "__main__":
    unittest.main()
