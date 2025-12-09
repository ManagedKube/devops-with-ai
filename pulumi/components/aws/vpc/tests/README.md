# VPC Component Unit Tests

This directory contains unit tests for the VPC Pulumi component.

## Overview

The tests validate the VPC component's behavior using Pulumi's mocking framework. No actual AWS resources are created during testing.

## Test Coverage

The test suite covers:

1. **Basic Creation**: VPC without NAT Gateways
2. **NAT Gateway Creation**: VPC with NAT Gateways enabled
3. **Custom VPC Name**: Using a custom name for the VPC
4. **Snake Case Parameters**: Support for both camelCase and snake_case parameter names
5. **Tagging**: Correct application of tags to resources
6. **Output Validation**: All expected outputs are present

## Setup

Create a virtual environment and install dependencies:

```bash
cd pulumi/components/aws/vpc
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-test.txt
```

## Running Tests

### Run all tests

```bash
python -m pytest tests/ -v
```

### Run a specific test

```bash
python -m pytest tests/test_vpc.py::TestVpc::test_basic_creation_without_nat_gateway -v
```

### Run with verbose output

```bash
python -m pytest tests/ -v -s
```

### Run with coverage

```bash
python -m pytest tests/ --cov=. --cov-report=html
```

## Test Structure

Each test follows this pattern:

1. **Setup**: Define test arguments with VPC configuration
2. **Execute**: Create the VPC component
3. **Verify**: Check outputs using assertions in an `apply` callback

Example:

```python
@pulumi.runtime.test
def test_basic_creation(self):
    """Test basic VPC creation."""
    # Setup
    args = {
        "vpcCidr": "10.0.0.0/16",
        "publicSubnetCidrs": ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"],
        # ... other args
    }
    
    # Execute
    component = Vpc("test-vpc", args)
    
    # Verify
    def check_outputs(outputs):
        vpc_id, vpc_arn = outputs
        self.assertIsNotNone(vpc_id)
        self.assertIn("vpc", vpc_id)
    
    return pulumi.Output.all(
        component.vpc_id,
        component.vpc_arn,
    ).apply(lambda args: check_outputs(args))
```

## Mock Implementation

The `MyMocks` class provides mock implementations for:

- VPC
- Subnets (public and private)
- Internet Gateway
- NAT Gateway
- Elastic IP
- Route Tables
- Routes
- Route Table Associations
- Security Groups

## Troubleshooting

### ImportError

If you get an import error, ensure `conftest.py` is present and the Python path is set correctly.

### Tests Hang

If tests hang, make sure test methods return the result of `pulumi.Output.all().apply()`.

### Mock Not Working

Verify all resource types used by the component are handled in `MyMocks.new_resource()`.

## References

- [Pulumi Unit Testing Guide](https://www.pulumi.com/docs/iac/guides/testing/unit/)
- [pytest Documentation](https://docs.pytest.org/)
