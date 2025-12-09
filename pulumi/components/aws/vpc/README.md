# VPC Component

A reusable Pulumi component for creating AWS VPC infrastructure with public and private subnets.

## Features

- **VPC**: Creates a VPC with configurable CIDR block and DNS support
- **Public Subnets**: Configurable number of public subnets (2-3 typical) across availability zones with auto-assign public IP
- **Private Subnets**: Configurable number of private subnets (2-3 typical) across availability zones
- **Internet Gateway**: For public subnet internet connectivity
- **Route Tables**: Properly configured route tables for public and private subnets
- **Default Security Group**: Allows all inbound and outbound traffic (configurable)
- **Optional NAT Gateways**: One NAT Gateway per availability zone for private subnet internet access
- **Flexible Subnet Count**: Supports 2 or 3 subnets (or more) - simply provide the desired number of CIDR blocks

## Usage

### In Pulumi YAML

```yaml
name: my-vpc
runtime: yaml
packages:
  vpc: https://github.com/ManagedKube/devops-with-ai.git/pulumi/components/aws/vpc@0.0.1

resources:
  my-vpc:
    type: vpc:index:Vpc
    properties:
      vpcCidr: "10.0.0.0/16"
      publicSubnetCidrs:
        - "10.0.1.0/24"
        - "10.0.2.0/24"
        - "10.0.3.0/24"
      privateSubnetCidrs:
        - "10.0.11.0/24"
        - "10.0.12.0/24"
        - "10.0.13.0/24"
      availabilityZones:
        - "us-west-2a"
        - "us-west-2b"
        - "us-west-2c"
      enableNatGateway: true
      vpcName: "my-application-vpc"
      tagsAdditional:
        Environment: "production"
        ManagedBy: "pulumi"
```

### In Python

```python
from vpc import Vpc

vpc = Vpc(
    "my-vpc",
    {
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
        "enableNatGateway": True,
        "vpcName": "my-application-vpc",
        "tagsAdditional": {
            "Environment": "production",
            "ManagedBy": "pulumi",
        },
    },
)

# Access outputs
vpc_id = vpc.vpc_id
public_subnet_ids = vpc.public_subnet_ids
private_subnet_ids = vpc.private_subnet_ids
```

### Example with 2 Subnets

You can create a VPC with just 2 subnets by providing 2 CIDR blocks:

```yaml
resources:
  my-vpc-two-subnets:
    type: vpc:index:Vpc
    properties:
      vpcCidr: "10.0.0.0/16"
      publicSubnetCidrs:
        - "10.0.1.0/24"
        - "10.0.2.0/24"
      privateSubnetCidrs:
        - "10.0.11.0/24"
        - "10.0.12.0/24"
      availabilityZones:
        - "us-east-1a"
        - "us-east-1b"
      enableNatGateway: false
      vpcName: "my-two-subnet-vpc"
      tagsAdditional:
        Environment: "development"
```

## Parameters

### Required Parameters

- **vpcCidr** (string): CIDR block for the VPC (e.g., "10.0.0.0/16")
- **publicSubnetCidrs** (list[string]): List of CIDR blocks for public subnets (e.g., 2-3 subnets)
- **privateSubnetCidrs** (list[string]): List of CIDR blocks for private subnets (e.g., 2-3 subnets)
- **availabilityZones** (list[string]): List of availability zones to use (must match the number of subnets)
- **tagsAdditional** (dict): Additional tags to apply to all resources

**Note**: The number of subnets is determined by the length of the `publicSubnetCidrs` list. Provide 2 CIDR blocks for 2 subnets, 3 for 3 subnets, etc.

### Optional Parameters

- **enableNatGateway** (boolean): Whether to create NAT Gateways in each private subnet. Default: `false`
- **vpcName** (string): Name for the VPC. If not provided, uses the resource name

## Outputs

- **vpc_id**: The ID of the VPC
- **vpc_arn**: The ARN of the VPC
- **public_subnet_ids**: List of public subnet IDs
- **private_subnet_ids**: List of private subnet IDs
- **internet_gateway_id**: The ID of the Internet Gateway
- **nat_gateway_ids**: List of NAT Gateway IDs (empty if NAT Gateways are disabled)
- **default_security_group_id**: The ID of the default security group

## Architecture

### Without NAT Gateways (enableNatGateway: false)

```
┌─────────────────────────────────────────────────────────────┐
│                           VPC                                │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Public       │  │ Public       │  │ Public       │      │
│  │ Subnet AZ-1  │  │ Subnet AZ-2  │  │ Subnet AZ-3  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                    ┌───────▼────────┐                        │
│                    │ Internet       │                        │
│                    │ Gateway        │                        │
│                    └────────────────┘                        │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Private      │  │ Private      │  │ Private      │      │
│  │ Subnet AZ-1  │  │ Subnet AZ-2  │  │ Subnet AZ-3  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### With NAT Gateways (enableNatGateway: true)

```
┌─────────────────────────────────────────────────────────────┐
│                           VPC                                │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Public       │  │ Public       │  │ Public       │      │
│  │ Subnet AZ-1  │  │ Subnet AZ-2  │  │ Subnet AZ-3  │      │
│  │ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │      │
│  │ │ NAT GW   │ │  │ │ NAT GW   │ │  │ │ NAT GW   │ │      │
│  │ └────┬─────┘ │  │ └────┬─────┘ │  │ └────┬─────┘ │      │
│  └──────┼───────┘  └──────┼───────┘  └──────┼───────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                    ┌───────▼────────┐                        │
│                    │ Internet       │                        │
│                    │ Gateway        │                        │
│                    └────────────────┘                        │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Private      │  │ Private      │  │ Private      │      │
│  │ Subnet AZ-1  │  │ Subnet AZ-2  │  │ Subnet AZ-3  │      │
│  │      ▲       │  │      ▲       │  │      ▲       │      │
│  │      │       │  │      │       │  │      │       │      │
│  └──────┼───────┘  └──────┼───────┘  └──────┼───────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│              Routes to respective NAT Gateway                │
└─────────────────────────────────────────────────────────────┘
```

## Testing

To run the unit tests:

```bash
cd pulumi/components/aws/vpc
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-test.txt
python -m pytest tests/ -v
```

See [tests/README.md](tests/README.md) for more information on testing.

## Notes

- The default security group allows all inbound and outbound traffic. This is suitable for development but should be restricted for production use.
- NAT Gateways incur additional costs. Only enable them if private subnets need internet access.
- The component creates one NAT Gateway per availability zone when enabled, providing high availability but at higher cost.
- All resources are tagged with the provided `tagsAdditional` for easy identification and cost tracking.
