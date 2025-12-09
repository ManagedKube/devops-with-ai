---
applyTo: "pulumi/components/**"
---
## What are these files for?
These are Pulumi components that we have written to encapsulate common infrastructure patterns we use in our Pulumi projects.

## When modifying Pulumi components
When adding or modifying Pulumi components in this directory, please follow these guidelines in this AGENT.md file: <repo root>/pulumi/components/AGENT.md

This file contains specific instructions for working with Pulumi components, including setup, testing, and deployment procedures. Make sure to read and adhere to these instructions to ensure consistency and quality across all Pulumi components in this repository.

If the component is modified in a PR, it must be tested first by a unit test (if one exist) AND then
the pulumi instantiation Pulumi.yaml file should be set to a relative path to the modified component
so that it can be tested in the PR.

## The Pulumi component API doc
When doing work and making changes to the component, always check with the docs at the following
link to make sure you are using the pulumi python api correctly:

https://www.pulumi.com/registry/packages/aws/api-docs/
