# Pulumi

## Set aws region

```
export AWS_REGION=us-east-1
```

## Create the bucket for the backend

Create a bucket:
```bash
aws s3api create-bucket --bucket managedkube-pulumi-staging2 --region us-east-1 --create-bucket-configuration LocationConstraint=us-east-1
```

## Login to s3 backend store

### staging
```bash
# Set the correct AWS region (bucket is in us-west-2)
export AWS_REGION=us-east-1
pulumi login s3://managedkube-pulumi-staging2/staging
```

## Pulumi Stack
Create a new stack:
```
pulumi stack init organization/<name of the stack>/staging
```
The word `organization` is static and cannot be changed.

The name of the stack is the `name` in the `Pulumi.yaml` file.

The Github Action will not run in a PR if it is a new stack that has not been inititialized.  You will get and error.

## Github Token
If your repository is private and you are using Pulumi components from there,
you will need to set a `GITHUB_TOKEN` so that Pulumi can access the private
repository and get the component.

```
export GITHUB_TOKEN=xxx
```
