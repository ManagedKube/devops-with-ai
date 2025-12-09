---
applyTo: "pulumi/components/**/tests/**"
---

# Pulumi Component Unit Testing Instructions

## Purpose
This file provides standardized guidelines for creating and maintaining unit tests for Pulumi components in this repository.

## Test Output Requirements

**ALWAYS output the unit test run results into the PR when a component is modified.**

When making changes to any Pulumi component:
1. Run the component's unit tests after making changes
2. Capture the full test output showing all test results
3. Include the test output in the PR description or as a comment
4. Ensure all tests are passing before finalizing the PR

Example test output format:
```
================================================= test session starts ==================================================
platform linux -- Python 3.12.3, pytest-9.0.1, pluggy-1.6.0
plugins: asyncio-1.3.0

tests/test_component.py::TestComponent::test_basic_creation PASSED                              [ 33%]
tests/test_component.py::TestComponent::test_with_feature PASSED                                [ 66%]
tests/test_component.py::TestComponent::test_without_feature PASSED                             [100%]

=================================================== 3 passed in 0.65s ==================================================
```

This provides visibility into test status and helps reviewers verify that changes don't break existing functionality.

## Test Structure

All Pulumi component tests should follow this standardized structure:

```
pulumi/components/aws/<component-name>/
├── __main__.py
├── <component-name>.py
├── requirements.txt
├── requirements-test.txt
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── README.md
    └── test_<component-name>.py
```

## Required Files

### tests/__init__.py
Simple package marker:
```python
# Test package for <component-name> component
```

### tests/conftest.py
Standard pytest configuration to set up import paths:
```python
import pytest
import sys
import os

# Add the parent directory to the Python path so tests can import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

### requirements-test.txt
Standard test dependencies:
```
pulumi>=3.130.0
pulumi-aws>=6.50.1
pytest>=7.4.0
pytest-asyncio>=0.21.0
```

### tests/README.md
Comprehensive documentation including:
- Overview of test coverage
- Setup instructions (virtual environment, dependencies)
- How to run tests (basic, verbose, specific test, with coverage)
- Test structure pattern
- Troubleshooting guide
- References to Pulumi testing documentation

See `pulumi/components/aws/sg/tests/README.md` or `pulumi/components/aws/vpc/tests/README.md` for examples.

## Test Implementation Pattern

### 1. Mock Class
Create a `MyMocks` class that implements `pulumi.runtime.Mocks`:

```python
class MyMocks(pulumi.runtime.Mocks):
    """
    Mock implementation for testing Pulumi resources without creating actual infrastructure.
    """
    
    def new_resource(self, args: pulumi.runtime.MockResourceArgs) -> tuple[str, dict[str, Any]]:
        """Handle resource creation mocks."""
        outputs = args.inputs
        
        # Add mock implementations for each resource type
        if args.typ == "aws:ec2/vpc:Vpc":
            outputs["id"] = f"vpc-{args.name}"
            outputs["arn"] = f"arn:aws:ec2:region:account:vpc/{outputs['id']}"
        
        return outputs.get("id", args.name), outputs
    
    def call(self, args: pulumi.runtime.MockCallArgs) -> dict[str, Any]:
        """Handle provider function call mocks."""
        return {}

# Set mocks for all tests
pulumi.runtime.set_mocks(MyMocks())
```

### 2. Test Class
Use `unittest.TestCase` with `@pulumi.runtime.test` decorator:

```python
class TestComponentName(unittest.TestCase):
    """Test cases for the ComponentName component."""
    
    @pulumi.runtime.test
    def test_basic_creation(self):
        """Test basic component creation."""
        import sys
        import os
        
        # Import component
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from component_name import ComponentName
        
        # Setup: Define test arguments
        args = {
            "param1": "value1",
            "param2": "value2",
        }
        
        # Execute: Create component
        component = ComponentName("test-component", args)
        
        # Verify: Check outputs
        def check_output(output_value):
            self.assertIsNotNone(output_value)
            self.assertEqual(output_value, "expected_value")
        
        return pulumi.Output.all(component.output).apply(
            lambda args: check_output(args[0])
        )
```

## Test Coverage Requirements

For each component, create tests that cover:

1. **Basic Creation**: Test component with minimal required parameters
2. **Optional Features**: Test each optional feature when enabled
3. **Default Behavior**: Verify defaults when optional parameters are omitted
4. **Tag Propagation**: Verify tags are correctly applied to resources
5. **Output Validation**: Check all component outputs are correctly set
6. **Edge Cases**: Test boundary conditions and error handling

## Running Tests

### From Component Directory
```bash
cd pulumi/components/aws/<component-name>
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-test.txt
python -m pytest tests/ -v
```

### Run Specific Test
```bash
python -m pytest tests/test_<component>.py::TestClass::test_method -v
```

### With Coverage
```bash
python -m pytest tests/ --cov=. --cov-report=html
```

## Best Practices

1. **Test Names**: Use descriptive names that clearly state what is being tested
   - Good: `test_vpc_with_flow_logs_enabled`
   - Bad: `test_feature1`

2. **Test Organization**: Group related tests in the same test class

3. **Assertions**: Use specific assertions
   - `self.assertEqual(actual, expected)` over `self.assertTrue(actual == expected)`
   - `self.assertIsNotNone(value)` over `self.assertTrue(value is not None)`

4. **Documentation**: Every test method should have a docstring explaining what it tests

5. **Independence**: Tests should be independent and not rely on execution order

6. **Mock All Resources**: Ensure `MyMocks.new_resource()` handles all AWS resource types created by your component

7. **Return Statements**: Always return the result of `pulumi.Output.all().apply()` for proper async handling

## Testing Optional Features

When testing optional features:
- Create one test with the feature enabled
- Create another test with the feature disabled (default)
- Verify outputs are `None` or empty when feature is disabled

Example:
```python
@pulumi.runtime.test
def test_with_optional_feature(self):
    """Test component with optional feature enabled."""
    args = {"enable_feature": True}
    component = Component("test", args)
    
    def check_feature(feature_output):
        self.assertIsNotNone(feature_output)
    
    return pulumi.Output.all(component.feature_output).apply(
        lambda args: check_feature(args[0])
    )

@pulumi.runtime.test
def test_without_optional_feature(self):
    """Test component with optional feature disabled."""
    args = {}  # Feature not enabled
    component = Component("test", args)
    
    self.assertIsNone(component.feature_output)
    # or verify in apply if it's an Output
```

## Troubleshooting

### ImportError
Ensure `conftest.py` is properly setting up the Python path.

### Tests Hang
Make sure test methods return the result of `pulumi.Output.all().apply()`.

### Mock Not Working
Verify all resource types used by the component are handled in `MyMocks.new_resource()`.

## References

- [Pulumi Unit Testing Guide](https://www.pulumi.com/docs/iac/guides/testing/unit/)
- [pytest Documentation](https://docs.pytest.org/)
- Example implementations:
  - `pulumi/components/aws/sg/tests/`
  - `pulumi/components/aws/vpc/tests/`
  - `pulumi/components/aws/dynamodb/tests/`
