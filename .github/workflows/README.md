# GitHub Actions Workflows

This directory contains the CI/CD workflows for automating Pulumi deployments.

## Workflows

### `pulumi_staging.yaml`
Manages Pulumi deployments to the staging environment.

**Triggers:**
- **Push to `main`**: Automatically runs `pulumi up` for staging when changes are merged
- **Pull Request**: Runs `pulumi preview` to show infrastructure changes
- **PR Comment**: Manually trigger `pulumi up` on staging via comment (see below)

**PR Comment Trigger:**
You can deploy changes to staging before merging by commenting on a PR:

```
/pulumi up
```

**Requirements:**
- You must be a repository collaborator with write or admin permissions
- The command must be posted as a comment on a pull request
- The exact command `/pulumi up` must be used (case-sensitive)

This will:
1. Detect the command and add a 🚀 reaction
2. Post an acknowledgment comment
3. Run `pulumi up` on the staging environment
4. Deploy the infrastructure changes from your PR branch

**Use Cases:**
- Test infrastructure changes in staging before merging
- Validate multi-step deployments
- Debug issues in a live environment

### `pulumi_prod.yaml`
Manages Pulumi deployments to the production environment.

**Triggers:**
- **Push to `main`**: Automatically runs `pulumi up` for production when changes are merged
- **Pull Request**: Runs `pulumi preview` to show infrastructure changes

## How It Works

Both workflows use a matrix strategy to:
1. Detect which directories have changed
2. Generate a matrix of affected Pulumi stacks
3. Run Pulumi operations (preview or up) on each stack in parallel

This ensures that only the infrastructure components that have changed are deployed, making the process faster and safer.

## Security

- All secrets are stored in GitHub Secrets and injected at runtime
- AWS credentials are configured per environment (staging vs production)
- Workflows use minimal permissions required for their operations
- Third-party actions should be pinned to specific commits (see `.github/instructions/actions.instructions.md`)
- **PR Comment Trigger Security**:
  - Only repository collaborators with write or admin permissions can trigger deployments via comments
  - The exact command `/pulumi up` is required to prevent accidental triggers
  - Permission checks are performed before any deployment actions are taken
  - Unauthorized users receive a clear error message

## Concurrency

Workflows use concurrency groups to ensure only one deployment runs at a time per branch, preventing race conditions and state file conflicts.

## Environment Configuration

Environment-specific configurations are managed through:
- **GitHub Variables**: Non-sensitive environment variables (e.g., `AWS_REGION`, `ECS_CLUSTER`)
- **GitHub Secrets**: Sensitive data (e.g., API keys, credentials)
- **Pulumi Config**: Stack-specific configuration in `Pulumi.yaml` and `Pulumi.<stack>.yaml` files
