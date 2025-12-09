# Pulumi Components

## Overview
The directories in this level holds Pulumi Components which are like modules or classes.  Each
one performs a function such as creating an infrastructure item or a set of items.  The user
will use these components and instantiate an instance of it.

## Tech stack
- **Infrastructure as Code**: Pulumi (Python runtime)

## Directory structure
The subfolders are named after each cloud providers and the components to create resources in
those cloud providers goes under that.

Under each cloud provider's directory are the components directory.  Each component's files will
be placed in there.

## Project and Code Guidelines

### Resource Tagging
- Add tags to all resources indicating:
  - What created the resource (e.g., `created_by: pulumi`)
  - The environment (e.g., `environment: staging`)
  - Any additional context from `tags_additional` parameter

### Pulumi Component Parameters
When adding input parameters to Pulumi components:
1. Always add type hints using `TypedDict`
2. Provide sensible default values when possible
3. Make parameters required (no default) only when there's no good default value
4. When suggesting code changes, include both:
   - The Python component code
   - Example YAML configuration for `Pulumi.yaml` file

## Component Releases
The `main` branch in this repository has the latest code that can be in various state
from working to not working.

We perform a Github Release and create a tag for the components to be used.  This allows us
to peg the code to a point in time where we know that it is working and if we re-run the
pulumi component the code that will run will point to that tag.  If we do not do this and
say use a relative path to the component, it might run fine the first time because we are
currently working on the component and know what code is there but when we re-run it sometime
in the future, we CAN NOT be certain if the code has changed and if we will get the same
results.

We use semver for versioning, example: v1.0.1.

A human has to perform a github release of a version.

## What uses these components
The folders [here](../environments/) holds the users instantiations of the components in the
sub directories here.

## Developing and Testing Pulumi Components

### Component Development Workflow

1. **Create a new branch** for your component changes

2. **Make changes to the component** (e.g., `pulumi/components/aws/rds/rds.py`)
   ```python
   # Example: Add new parameter
   instance_args["manage_master_user_password"] = args.get("manage_master_user_password", True)
   ```

3. **Test locally** (optional) by referencing the component with a relative path:
   ```yaml
   packages:
     rds: ../../../../../components/aws/rds@0.0.0
   ```

4. **Create a pre-release** in GitHub Releases:
   - Check the "pre-release" box
   - Use semantic versioning (major.minor.patch)
   - Increment patch version from previous release

5. **Update test environment** to use the new version:
   - Edit `Pulumi.yaml` in test environment (e.g., `pulumi/environments/aws/staging/60-rds/10-core/Pulumi.yaml`)
   ```yaml
   packages:
     rds: https://github.com/ManagedKube/devops-with-ai.git/pulumi/components/aws/rds@1.0.2
   ```
   - Update SDK version file if present (e.g., rename and update `sdks/managedkube-rds/rds-1.0.2.yaml`)

6. **Test in PR**: GitHub Actions will run `pulumi preview` with the new component

7. **Optional: Test `pulumi up` in non-prod**:
   - Temporarily change workflow from `preview` to `up` in PR (for testing only)
   - ⚠️ Remember to change back to `preview` before merging!

8. **Merge**: Once validated, merge the PR and promote to full release

## When a Pulumi Component is added or modified
When a user or the AI agent has decided that a Pulumi component has to be added or modified you should do or recommend the following.

### Step 1: Add or edit the component
Make the necessary changes by either adding a new component or modifying a current one

### Step 2: Test it out in a PR with a local path
In the user instantiation of the component in `pulumi/environments/**/Pulumi.yaml`
use a local path to point to the component that was added or modified in step 1

```yaml
name: my_pulumi
description: An example of a user instantiation of pulumi with a component that resides in this repository
runtime: yaml
packages:
  mycomponent: ../../../../../components/aws/mycomponent@0.0.0
```

* mycomponent is an example component name
* the path to the component is a relative path to the component.  From the directory of this 
  Pulumi.yaml  file you should be able to ls this path and get the components directory listing successfully
* The version for a local component is set to 0.0.0

The AI agent should then run the following as a test to make sure it can add the pulumi component that was just created or modified:
1. change directory to the component's directory
1. run: python -m venv venv
1. run: source venv/bin/activate
1. run: pip install -r requirements.txt
1. Then change to the directory where the Pulumi.yaml file is that is using this local component
1. run: pulumi package add "to the path of the components directory in step 1"
1. The command in the previous step created a new file in the sdks folder.   Add this file to the PR.
1. Post your results back to the PR

### Step 3: Let the user run the pulumi preview in the PR
Summarize the steps above that and let the user know what you have done and why.  Then ask the user to run the github action workflow in the PR to test this out.

This will be the development cycle for adding a new pulumi component or modifying one.  Repeat step 1
to 3 here until the user is satified with the outcome.

### Step 4: Set it back to to be merged
Once the user is satified with the outcome, you should aks if they are satisfied.  We can NOT merge
with the component pointing to a local path.  You will have to:

1. Ask the user to perform a github release based on the branch in this PR and ask the user
   to give you this new tagged version
1. Once the user has given you the tagged version, for example if they post back something like
   v1.0.32 or 1.0.32.  You will take this and perform the following steps
1. Set the user instantiation Pulumi.yaml file to this version:
   ```yaml
   name: my_pulumi
   description: An example of a user instantiation of pulumi with a component that resides in this repository
   runtime: yaml
   packages:
   mycomponent: https://github.com/ManagedKube/devops-with-ai.git/pulumi/components/aws/mycomponent@1.032
   ```
1. Then delete the file in the `sdks` folder that was for the local version with 0.0.0.  File would be in
   this format: `./sdks/mycomponent/mycomponent-0.0.0.yaml`
1. Add in the file that points to the new version: `./sdks/managedkube-mycomponent/mycomponent-1.0.32.yaml`
   ```yaml
   packageDeclarationVersion: 1
   name: mycomponent
   version: 1.0.32
   downloadUrl: git://github.com/ManagedKube/devops-with-ai.git/pulumi/components/aws/mycomponent
   ```

After this has been completed, then you should let the user know:
* They should let the pulumi preview staging workflow run to test it out
* They can run `/pulumi up` to fully test it with the new github release 
* Tt is good to merge now.

## Imports not to use
Do not use the following python imports:
* NotRequired
