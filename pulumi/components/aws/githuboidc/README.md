# GitHub Actions OIDC Provider Component

This Pulumi component automates the setup of an AWS IAM OIDC Identity Provider for GitHub Actions, based on [GitHub's OIDC AWS documentation](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws).

## Overview

The component creates:
- An IAM OIDC Identity Provider configured for GitHub Actions
- An IAM Role that trusts the OIDC provider
- Support for repository and branch filtering for security
- Optional managed policy attachments
- Optional inline policy attachments

## Usage

### Basic Usage (All Branches)

```yaml
name: github-oidc
runtime: yaml
packages:
  githuboidc: https://github.com/malloryai/infrastructure.git/pulumi/components/aws/githuboidc@1.0.0
resources:
  githubOidcProvider:
    type: githuboidc:index:Githuboidc
    properties:
      roleName: github-actions-deployment-role
      repositories:
        - "malloryai/infrastructure"
      thumbprint: "2b18947a6a9fc7764fd8b5fb18a863b0c6dac24f"
      tagsAdditional:
        environment: staging
outputs:
  oidc_provider_arn: ${githubOidcProvider.oidcProviderArn}
  role_arn: ${githubOidcProvider.roleArn}
  role_name: ${githubOidcProvider.roleName}
```

### With Specific Branches

Restrict the role to specific branches:

```yaml
githubOidcProvider:
  type: githuboidc:index:Githuboidc
  properties:
    roleName: github-actions-deployment-role
    repositories:
      - "malloryai/infrastructure"
    thumbprint: "2b18947a6a9fc7764fd8b5fb18a863b0c6dac24f"
    branches:
      - "main"
      - "develop"
    tagsAdditional:
      environment: production
```

### With GitHub Environments

Restrict the role to specific GitHub environments:

```yaml
githubOidcProvider:
  type: githuboidc:index:Githuboidc
  properties:
    roleName: github-actions-deployment-role
    repositories:
      - "malloryai/infrastructure"
    thumbprint: "2b18947a6a9fc7764fd8b5fb18a863b0c6dac24f"
    environments:
      - "production"
      - "staging"
    tagsAdditional:
      environment: production
```

### With Policy Attachments

Attach AWS managed policies to the role:

```yaml
githubOidcProvider:
  type: githuboidc:index:Githuboidc
  properties:
    roleName: github-actions-deployment-role
    repositories:
      - "malloryai/infrastructure"
    thumbprint: "2b18947a6a9fc7764fd8b5fb18a863b0c6dac24f"
    policyArns:
      - "arn:aws:iam::aws:policy/AdministratorAccess"
    tagsAdditional:
      environment: staging
```

### Multiple Repositories

Allow multiple repositories to assume the role:

```yaml
githubOidcProvider:
  type: githuboidc:index:Githuboidc
  properties:
    roleName: github-actions-deployment-role
    repositories:
      - "malloryai/infrastructure"
      - "malloryai/core"
      - "malloryai/web"
    thumbprint: "2b18947a6a9fc7764fd8b5fb18a863b0c6dac24f"
    tagsAdditional:
      environment: staging
```

### With Inline Policies

Add custom inline policies:

```yaml
githubOidcProvider:
  type: githuboidc:index:Githuboidc
  properties:
    roleName: github-actions-deployment-role
    repositories:
      - "malloryai/infrastructure"
    thumbprint: "2b18947a6a9fc7764fd8b5fb18a863b0c6dac24f"
    inlinePolicies:
      - name: custom-s3-access
        policy: |
          {
            "Version": "2012-10-17",
            "Statement": [
              {
                "Effect": "Allow",
                "Action": [
                  "s3:GetObject",
                  "s3:PutObject"
                ],
                "Resource": "arn:aws:s3:::my-bucket/*"
              }
            ]
          }
    tagsAdditional:
      environment: staging
```

## Parameters

### Required Parameters

- `roleName` (string): The name of the IAM role to create
- `repositories` (list): List of GitHub repositories in "owner/repo" format
- `thumbprint` (string): The thumbprint of the GitHub OIDC provider certificate
- `tagsAdditional` (dict): Additional tags to apply to all resources

### Optional Parameters

- `branches` (list): List of branch names to restrict access (default: ["*"] for all)
- `environments` (list): List of GitHub environment names to restrict access
- `policyArns` (list): List of managed policy ARNs to attach to the role
- `inlinePolicies` (list): List of inline policies to attach

## Outputs

- `oidcProviderArn`: The ARN of the OIDC Identity Provider
- `roleArn`: The ARN of the IAM role
- `roleName`: The name of the IAM role

## Using with GitHub Actions

After deploying this component, configure your GitHub Actions workflow:

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write   # Required for OIDC
      contents: read
    steps:
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-actions-deployment-role
          aws-region: us-east-1
      
      - name: Verify Identity
        run: aws sts get-caller-identity
```

## Security Considerations

- **Repository Filtering**: The role is restricted to specific repositories
- **Branch Filtering**: Optionally restrict to specific branches
- **Environment Filtering**: Optionally restrict to GitHub environments
- **Least Privilege**: Only attach the minimum required policies
- **Audit**: Regularly review CloudTrail logs for role assumption events

## GitHub OIDC Details

- **OIDC Provider URL**: https://token.actions.githubusercontent.com
- **Audience**: sts.amazonaws.com
- **Subject Format**: repo:owner/repo:ref:refs/heads/branch or repo:owner/repo:*

## References

- [GitHub OIDC AWS Documentation](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws)
- [AWS IAM OIDC Identity Providers](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html)
- [Pulumi AWS IAM Documentation](https://www.pulumi.com/registry/packages/aws/api-docs/iam/)
