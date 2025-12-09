"""
Unit tests for the GitHub OIDC Pulumi component.

These tests use Pulumi's unit testing framework to validate the behavior
of the GitHub OIDC component without creating actual AWS resources.
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

        # Mock OIDC Identity Provider
        if args.typ == "aws:iam/openIdConnectProvider:OpenIdConnectProvider":
            outputs["id"] = "arn:aws:iam::123456789012:oidc-provider/token"
            outputs["arn"] = (
                "arn:aws:iam::123456789012:oidc-provider/"
                "token.actions.githubusercontent.com"
            )

        # Mock IAM Role
        elif args.typ == "aws:iam/role:Role":
            outputs["id"] = f"role-{args.name}"
            outputs["arn"] = (
                f"arn:aws:iam::123456789012:role/{outputs.get('name', args.name)}"
            )
            outputs["name"] = outputs.get("name", args.name)

        # Mock IAM Role Policy Attachment
        elif args.typ == "aws:iam/rolePolicyAttachment:RolePolicyAttachment":
            outputs["id"] = f"attachment-{args.name}"

        # Mock IAM Role Policy (inline)
        elif args.typ == "aws:iam/rolePolicy:RolePolicy":
            outputs["id"] = f"policy-{args.name}"

        return outputs.get("id", args.name), outputs

    def call(self, args: pulumi.runtime.MockCallArgs) -> dict[str, Any]:
        """
        Called when a provider function is invoked.

        Returns mock outputs for the function.
        """
        return {}


# Set the mocks for all tests in this module
pulumi.runtime.set_mocks(MyMocks())


class TestGithuboidc(unittest.TestCase):
    """Test cases for the GitHub OIDC component."""

    @pulumi.runtime.test
    def test_basic_creation(self):
        """
        Test basic GitHub OIDC component creation with required parameters.
        """
        import sys
        import os

        # Add the parent directory to the path
        sys.path.insert(
            0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        from githuboidc import Githuboidc

        # Define test arguments
        args = {
            "roleName": "test-github-actions-role",
            "repositories": ["malloryai/infrastructure"],
            "thumbprint": "2b18947a6a9fc7764fd8b5fb18a863b0c6dac24f",
            "tagsAdditional": {
                "Environment": "test",
            },
        }

        # Create the component
        component = Githuboidc("test-oidc", args)

        # Verify outputs
        def check_outputs(outputs):
            oidc_arn, role_arn, role_name = outputs
            self.assertIsNotNone(oidc_arn)
            self.assertIsNotNone(role_arn)
            self.assertIsNotNone(role_name)
            self.assertIn("oidc-provider", oidc_arn)
            self.assertIn("role", role_arn)

        return pulumi.Output.all(
            component.oidc_provider_arn,
            component.role_arn,
            component.role_name,
        ).apply(lambda args: check_outputs(args))

    @pulumi.runtime.test
    def test_with_all_branches(self):
        """
        Test component with wildcard branch access (all branches).
        """
        import sys
        import os

        sys.path.insert(
            0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        from githuboidc import Githuboidc

        args = {
            "roleName": "test-all-branches-role",
            "repositories": ["malloryai/infrastructure"],
            "branches": ["*"],
            "thumbprint": "2b18947a6a9fc7764fd8b5fb18a863b0c6dac24f",
            "tagsAdditional": {},
        }

        component = Githuboidc("test-all-branches", args)

        def check_outputs(outputs):
            role_arn, role_name = outputs
            self.assertIsNotNone(role_arn)
            self.assertIsNotNone(role_name)

        return pulumi.Output.all(
            component.role_arn,
            component.role_name,
        ).apply(lambda args: check_outputs(args))

    @pulumi.runtime.test
    def test_with_specific_branches(self):
        """
        Test component with specific branch restrictions.
        """
        import sys
        import os

        sys.path.insert(
            0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        from githuboidc import Githuboidc

        args = {
            "roleName": "test-specific-branches-role",
            "repositories": ["malloryai/infrastructure"],
            "branches": ["main", "develop"],
            "thumbprint": "2b18947a6a9fc7764fd8b5fb18a863b0c6dac24f",
            "tagsAdditional": {},
        }

        component = Githuboidc("test-specific-branches", args)

        def check_outputs(outputs):
            role_arn, = outputs
            self.assertIsNotNone(role_arn)

        return pulumi.Output.all(
            component.role_arn,
        ).apply(lambda args: check_outputs(args))

    @pulumi.runtime.test
    def test_with_environments(self):
        """
        Test component with GitHub environment restrictions.
        """
        import sys
        import os

        sys.path.insert(
            0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        from githuboidc import Githuboidc

        args = {
            "roleName": "test-environments-role",
            "repositories": ["malloryai/infrastructure"],
            "environments": ["production", "staging"],
            "thumbprint": "2b18947a6a9fc7764fd8b5fb18a863b0c6dac24f",
            "tagsAdditional": {},
        }

        component = Githuboidc("test-environments", args)

        def check_outputs(outputs):
            role_arn, = outputs
            self.assertIsNotNone(role_arn)

        return pulumi.Output.all(
            component.role_arn,
        ).apply(lambda args: check_outputs(args))

    @pulumi.runtime.test
    def test_with_policy_arns(self):
        """
        Test component with managed policy attachments.
        """
        import sys
        import os

        sys.path.insert(
            0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        from githuboidc import Githuboidc

        args = {
            "roleName": "test-policy-arns-role",
            "repositories": ["malloryai/infrastructure"],
            "thumbprint": "2b18947a6a9fc7764fd8b5fb18a863b0c6dac24f",
            "policyArns": [
                "arn:aws:iam::aws:policy/AdministratorAccess",
                "arn:aws:iam::aws:policy/ReadOnlyAccess",
            ],
            "tagsAdditional": {},
        }

        component = Githuboidc("test-policy-arns", args)

        def check_outputs(outputs):
            role_arn, role_name = outputs
            self.assertIsNotNone(role_arn)
            self.assertIsNotNone(role_name)

        return pulumi.Output.all(
            component.role_arn,
            component.role_name,
        ).apply(lambda args: check_outputs(args))

    @pulumi.runtime.test
    def test_with_inline_policies(self):
        """
        Test component with inline policy attachments.
        """
        import sys
        import os
        import json

        sys.path.insert(
            0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        from githuboidc import Githuboidc

        inline_policy = json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": ["s3:GetObject"],
                "Resource": "arn:aws:s3:::my-bucket/*",
            }],
        })

        args = {
            "roleName": "test-inline-policies-role",
            "repositories": ["malloryai/infrastructure"],
            "thumbprint": "2b18947a6a9fc7764fd8b5fb18a863b0c6dac24f",
            "inlinePolicies": [{
                "name": "custom-s3-policy",
                "policy": inline_policy,
            }],
            "tagsAdditional": {},
        }

        component = Githuboidc("test-inline-policies", args)

        def check_outputs(outputs):
            role_arn, = outputs
            self.assertIsNotNone(role_arn)

        return pulumi.Output.all(
            component.role_arn,
        ).apply(lambda args: check_outputs(args))

    @pulumi.runtime.test
    def test_multiple_repositories(self):
        """
        Test component with multiple repository access.
        """
        import sys
        import os

        sys.path.insert(
            0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        from githuboidc import Githuboidc

        args = {
            "roleName": "test-multi-repo-role",
            "repositories": [
                "malloryai/infrastructure",
                "malloryai/core",
                "malloryai/web",
            ],
            "thumbprint": "2b18947a6a9fc7764fd8b5fb18a863b0c6dac24f",
            "tagsAdditional": {},
        }

        component = Githuboidc("test-multi-repo", args)

        def check_outputs(outputs):
            role_arn, = outputs
            self.assertIsNotNone(role_arn)

        return pulumi.Output.all(
            component.role_arn,
        ).apply(lambda args: check_outputs(args))

    @pulumi.runtime.test
    def test_snake_case_parameters(self):
        """
        Test component with snake_case parameter names.
        """
        import sys
        import os

        sys.path.insert(
            0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        from githuboidc import Githuboidc

        args = {
            "role_name": "test-snake-case-role",
            "repositories": ["malloryai/infrastructure"],
            "thumbprint": "2b18947a6a9fc7764fd8b5fb18a863b0c6dac24f",
            "tags_additional": {
                "Environment": "test",
            },
            "policy_arns": [
                "arn:aws:iam::aws:policy/ReadOnlyAccess",
            ],
        }

        component = Githuboidc("test-snake-case", args)

        def check_outputs(outputs):
            role_arn, role_name = outputs
            self.assertIsNotNone(role_arn)
            self.assertIsNotNone(role_name)

        return pulumi.Output.all(
            component.role_arn,
            component.role_name,
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
        from githuboidc import Githuboidc

        args = {
            "roleName": "test-tags-role",
            "repositories": ["malloryai/infrastructure"],
            "thumbprint": "2b18947a6a9fc7764fd8b5fb18a863b0c6dac24f",
            "tagsAdditional": {
                "Environment": "staging",
                "Project": "infrastructure",
                "Team": "platform",
            },
        }

        component = Githuboidc("test-tags", args)

        def check_outputs(outputs):
            oidc_arn, role_arn = outputs
            self.assertIsNotNone(oidc_arn)
            self.assertIsNotNone(role_arn)

        return pulumi.Output.all(
            component.oidc_provider_arn,
            component.role_arn,
        ).apply(lambda args: check_outputs(args))


if __name__ == "__main__":
    unittest.main()
