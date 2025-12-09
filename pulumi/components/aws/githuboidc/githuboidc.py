"""
GitHub OIDC provider and IAM role for AWS authentication.

This module creates an AWS IAM OIDC provider and role that allows GitHub Actions
to authenticate with AWS using OpenID Connect (OIDC) instead of static credentials.

Based on GitHub's OIDC documentation:
https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws
"""
from typing import Optional, TypedDict

import pulumi
from pulumi import ResourceOptions
from pulumi_aws import iam


class GithuboidcArgs(TypedDict, total=False):
    """Arguments for creating a GitHub Actions OIDC provider and IAM role.

    Required fields:
        roleName: The name of the IAM role to create.
        tagsAdditional: Additional tags to apply to resources.
        repositories: List of GitHub repositories allowed to assume the role.
            Format: "owner/repo" (e.g., "malloryai/infrastructure").
        thumbprint: The thumbprint of the GitHub OIDC provider certificate.
            This is required for AWS to validate the OIDC provider.

    Optional fields:
        policyArns: List of managed policy ARNs to attach to the role.
        inlinePolicies: List of inline policies with 'name' and 'policy' fields.
        branches: List of branch patterns to restrict access.
            Examples: ["main"], ["*"] for all branches.
            Default: ["*"] (all branches).
        environments: List of GitHub environment names to restrict access.
            If not specified, no environment restriction is applied.

    Based on GitHub's OIDC documentation:
        - Provider URL: https://token.actions.githubusercontent.com
        - Audience: sts.amazonaws.com
    """

    roleName: pulumi.Input[str]
    tagsAdditional: pulumi.Input[dict[str, pulumi.Input[str]]]
    repositories: pulumi.Input[list[pulumi.Input[str]]]
    thumbprint: pulumi.Input[str]
    branches: Optional[pulumi.Input[list[pulumi.Input[str]]]]
    environments: Optional[pulumi.Input[list[pulumi.Input[str]]]]
    policyArns: Optional[pulumi.Input[list[pulumi.Input[str]]]]
    inlinePolicies: Optional[pulumi.Input[list[dict[str, pulumi.Input[str]]]]]


class Githuboidc(pulumi.ComponentResource):
    """Creates an AWS IAM OIDC provider and role for GitHub Actions.

    This component automates the setup described in GitHub's OIDC AWS docs.
    It creates:
        - An IAM OIDC Identity Provider for GitHub Actions
        - An IAM Role that trusts the OIDC provider
        - Policy attachments for the role
    """

    oidc_provider_arn: pulumi.Output[str]
    role_arn: pulumi.Output[str]
    role_name: pulumi.Output[str]

    def __init__(
        self,
        name: str,
        args: GithuboidcArgs,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        """Initialize the GitHub OIDC component.

        Args:
            name: The unique name for this component instance.
            args: Configuration arguments for the OIDC provider and role.
            opts: Optional Pulumi resource options.
        """
        super().__init__('githuboidc:index:Githuboidc', name, {}, opts)

        # Helper to read snake_case or camelCase keys
        def pick(d: dict, snake: str, camel: str):
            """Get value from dict supporting both snake_case and camelCase."""
            return d.get(snake, d.get(camel))

        # Get required parameters (support both snake_case and camelCase)
        role_name = pick(args, "role_name", "roleName")
        tags_additional = pick(args, "tags_additional", "tagsAdditional") or {}
        repositories = pick(args, "repositories", "repositories") or []

        # Get optional parameters with defaults
        branches = pick(args, "branches", "branches") or ["*"]
        environments = pick(args, "environments", "environments")

        # Get thumbprint (required parameter)
        thumbprint = pick(args, "thumbprint", "thumbprint")

        # GitHub OIDC provider URL (fixed for all GitHub Actions)
        github_oidc_url = "https://token.actions.githubusercontent.com"

        # GitHub OIDC audience for AWS
        github_audience = "sts.amazonaws.com"

        # Create the OIDC Identity Provider
        provider_name = f"{role_name}-oidc-provider" if role_name else (
            "github-actions-oidc-provider"
        )
        oidc_tags = {
            "Name": provider_name,
            **tags_additional,
        }

        oidc_provider = iam.OpenIdConnectProvider(
            "github-oidc-provider",
            url=github_oidc_url,
            client_id_lists=[github_audience],
            thumbprint_lists=[thumbprint],
            tags=oidc_tags,
            opts=ResourceOptions(parent=self),
        )

        # Build the assume role policy document
        def create_assume_role_policy(inputs) -> str:
            """Create the IAM trust policy for GitHub OIDC.

            Args:
                inputs: Tuple of (provider_arn, repos, branch_list, env_list).

            Returns:
                JSON string of the trust policy document.
            """
            import json
            provider_arn, repos, branch_list, env_list = inputs

            # Create subject patterns for repository access
            # Format: repo:owner/repo:ref:refs/heads/branch or
            # repo:owner/repo:* for all refs
            sub_values = []
            for repo in repos:
                if branch_list and "*" not in branch_list:
                    # Specific branch restrictions
                    for branch in branch_list:
                        sub_values.append(
                            f"repo:{repo}:ref:refs/heads/{branch}"
                        )
                elif env_list:
                    # Environment restrictions
                    for env in env_list:
                        sub_values.append(f"repo:{repo}:environment:{env}")
                else:
                    # All branches/refs allowed
                    sub_values.append(f"repo:{repo}:*")

            # Use StringLike for wildcard patterns
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Federated": provider_arn},
                        "Action": "sts:AssumeRoleWithWebIdentity",
                        "Condition": {
                            "StringEquals": {
                                "token.actions.githubusercontent.com:aud": (
                                    github_audience
                                )
                            },
                            "StringLike": {
                                "token.actions.githubusercontent.com:sub": (
                                    sub_values
                                )
                            },
                        },
                    }
                ],
            }
            return json.dumps(policy)

        assume_role_policy = pulumi.Output.all(
            oidc_provider.arn, repositories, branches, environments
        ).apply(create_assume_role_policy)

        # Create the IAM role
        role_tags = {
            "Name": role_name,
            **tags_additional,
        }

        role = iam.Role(
            "github-role",
            name=role_name,
            assume_role_policy=assume_role_policy,
            tags=role_tags,
            opts=ResourceOptions(parent=self),
        )

        # Attach managed policies if provided
        policy_arns = pick(args, "policy_arns", "policyArns") or []
        for i, policy_arn in enumerate(policy_arns):
            if policy_arn:  # Skip None or empty values
                iam.RolePolicyAttachment(
                    f"github-role-policy-attachment-{i}",
                    role=role.name,
                    policy_arn=policy_arn,
                    opts=ResourceOptions(parent=self),
                )

        # Attach inline policies if provided
        inline_policies = pick(args, "inline_policies", "inlinePolicies") or []
        for i, policy in enumerate(inline_policies):
            if policy:  # Skip None or empty values
                # Use a safe resource name, fallback to indexed name
                resource_name = f"inline-policy-{i}"
                iam.RolePolicy(
                    resource_name,
                    name=policy.get("name"),
                    role=role.name,
                    policy=policy.get("policy"),
                    opts=ResourceOptions(parent=self),
                )

        self.oidc_provider_arn = oidc_provider.arn
        self.role_arn = role.arn
        self.role_name = role.name

        self.register_outputs({
            'oidc_provider_arn': oidc_provider.arn,
            'role_arn': role.arn,
            'role_name': role.name,
        })
