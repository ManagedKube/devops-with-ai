# GitHub OIDC Component Unit Tests

This directory contains unit tests for the GitHub OIDC Pulumi component using Pulumi's unit testing framework.

## Overview

These tests validate the behavior of the GitHub OIDC component without creating actual AWS resources. They use Pulumi's mocking framework to intercept resource creation calls and test the component's logic.

## Test Coverage

The test suite covers:

- ✅ Basic component creation with required parameters
- ✅ Wildcard branch access (all branches)
- ✅ Specific branch restrictions
- ✅ GitHub environment restrictions
- ✅ Managed policy attachments
- ✅ Inline policy attachments
- ✅ Multiple repository access
- ✅ Support for both snake_case and camelCase parameter naming
- ✅ Tag application and propagation

## Setup

### Prerequisites

- Python 3.8 or higher
- pip or pip3

### Installation

1. Navigate to the githuboidc component directory:
   ```bash
   cd pulumi/components/aws/githuboidc
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/macOS
   # or
   venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements-test.txt
   ```

## Running Tests

### Run All Tests

From the githuboidc component directory (`pulumi/components/aws/githuboidc`):

```bash
python -m pytest tests/ -v
```

### Run Specific Test

```bash
python -m pytest tests/test_githuboidc.py::TestGithuboidc::test_basic_creation -v
```

### Run Tests with Coverage

```bash
python -m pytest tests/ --cov=. --cov-report=html
```

## Test Structure

Each test follows this pattern:

1. **Setup**: Define test arguments (inputs to the component)
2. **Execute**: Create the component with test inputs
3. **Verify**: Check that outputs match expected values

Example:
```python
@pulumi.runtime.test
def test_basic_creation(self):
    # Setup
    args = {
        "roleName": "test-role",
        "repositories": ["org/repo"],
        "thumbprint": "...",
        "tagsAdditional": {},
    }
    
    # Execute
    component = Githuboidc("test", args)
    
    # Verify
    def check_outputs(outputs):
        self.assertIsNotNone(outputs[0])
    
    return pulumi.Output.all(component.role_arn).apply(check_outputs)
```

## Adding New Tests

When adding new functionality to the GitHub OIDC component:

1. Create a new test method in `tests/test_githuboidc.py`
2. Use the `@pulumi.runtime.test` decorator
3. Follow the setup-execute-verify pattern
4. Use descriptive test names that explain what is being tested
5. Add appropriate assertions to validate behavior

## Troubleshooting

### ImportError: No module named 'githuboidc'

Make sure you're running tests from the component directory or that the path is correctly set in `conftest.py`.

### Tests Hanging or Timing Out

Ensure that all test methods using `@pulumi.runtime.test` return the result of `pulumi.Output.all().apply()` for proper async handling.

### Mock Resources Not Working

Verify that the `MyMocks` class in `test_githuboidc.py` handles all resource types created by your component.

## References

- [Pulumi Unit Testing Guide](https://www.pulumi.com/docs/iac/guides/testing/unit/)
- [Pulumi Python Testing](https://www.pulumi.com/docs/iac/languages-sdks/python/testing/)
- [pytest Documentation](https://docs.pytest.org/)
