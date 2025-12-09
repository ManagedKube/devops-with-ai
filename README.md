# devops-with-ai
This repository is here to showcase how we are using Github Copilot Agent
to help build cloud infrastructure.

We have worked over a bunch of iterations with various AGENTS.md and various
Github instructions files to add more context on how we are building
infrastructure and how we like our code to be laid out.  It is very much
still an on going process but it is in a state where this setup is very
GOOD now.

## What do we mean by very good?
We can open a Github Issue and assign the agent a tasks and it can mostly
go off and do it on it's own and create a PR for us to look at and review.

In this setup, we have modules/components/classes that encapsulate major
infrastructure pieces.  For example, everyone needs a VPC but it contains
more than just a VPC.  It might have public subnets, private subnets, route
tables, default security groups, NAT, etc.  These are re-usable items across
environments which are then released as a Github Release, versioning it so
that we can duplicate environments reliably.

The agents here understands this and follows this pattern.  It also follows
a pattern where we want to test the modules/component changes in a PR before
creating a release.  It writes and runs unit tests on the modules.

This gives us a very good process to work out a new thing or a change in a PR,
and fully testing it before merging and creating a release of it that can be
duplicated to higher environments.

## Example Issue that the Github Copilot Agent completed

### Creating a VPC component
Issue link: https://github.com/ManagedKube/devops-with-ai/issues/1

Here is an issue where an Issue was opened for the agent to create
a VPC and if you follow it through to the PR, it will show you how
I interacted with it to make a few change and to debug an issue which
ultimately was not an issue but a cloud/IaC issue, that the agent pointed
out and told me how to fix it.
