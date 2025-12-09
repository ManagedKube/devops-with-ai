# environments
Each infrastructure environment is built on a cloud and has a name which is arbitrary but
we tend to stick with fairly conventional naming of the environment to staging and prod.

The Pulumi Components defined [here](../components/) are used in these environments.

### Required Before Each Commit
- Run `pulumi preview` before committing any changes to ensure what was changed is in a
  working state
- The `pulumi preview` runs in a PR and if you are in a PR look at the output of this run
  for any errors.  If there are any errors, report it and try to fix it.

## Note to the user
If a change can NOT be changed in place and it requires a delete and recreation of the item for the change to take affect, then you should tell the user this and make it clear up front and the first thing that is replied to the user so that they know.

## Directory structure
The directory structure is fairly flexible and can accommodate various use cases.  

Some features of the directory structure:
* There are numbers in front of the name of the directory, this is to help with ordering
  the creation of each resource.  The resources with the lowest number must be created
  first before the higher number ones.  Each folder level is its own ordered list.

Example of an AWS environment:
```
pulumi/environments
├── AGENTS.md
└── aws                                       <-- The cloud that the environment is on
    ├── prod                                  <-- A named environment
    │   ├── 40-vpc                            <-- An ordered list of cloud resources
    │   │   ├── Pulumi.prod.yaml              <-- Pulumi file
    │   │   ├── Pulumi.yaml                   <-- Pulumi yaml file
    │   │   └── sdks
    │   │       └── managedkube-vpc
    │   │           └── vpc-0.0.12.yaml       <-- Pulumi component version file
...
...
...
    └── staging                               <-- A named environment
        ├── 40-vpc
        │   ├── Pulumi.staging.yaml
        │   ├── Pulumi.yaml
        │   └── sdks
        │       └── managedkube-vpc
        │           └── vpc-0.0.12.yaml
...
...
...
        └── 90-ecs                            <-- Folder holding a group of cloud resources
            └── 10-core                       <-- Folder holding a group of cloud resources
                ├── 10-cluster                <-- The cloud resource
                │   ├── Pulumi.staging.yaml
                │   ├── Pulumi.yaml
                │   └── sdks
```

## Pulumi usage
We are using pulumi yaml to instantiate cloud resources.  The pulumi yaml can reference the
components that we have built [here](../components/) or use any pulumi compatible components.

The `Pulumi.yaml` file holds:
* name, description, runtime
* the packages used and the components
* the input values
* the output values


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

## Local development
When a human is developing locally on their computer they can reference a component with a local
path if they are making changes to that component and want to test the changes.

**Component Versioning:**
For use in a github action, in a pull request, or a named environment.

IMPORTANT: For any named environment, all components should reference a github release version.

Components should be versioned via a GitHub Releases:
```yaml
packages:
  alb: https://github.com/ManagedKube/devops-with-ai.git/pulumi/components/aws/alb@0.0.8
```

Whenever there is a change to the version number in the Pulumi.yaml file for a component,
the file in the `sdks` folder for that component MUST also be changed to match it.  There
should be ONLY ONE corresponding sdks folder and file for each component.

## Configuration Management

### Using GitHub Actions for Configuration
All production configuration is managed through GitHub Actions to avoid local setup requirements.

**Configuration Flow:**
1. Secrets and variables are stored in GitHub repository settings
2. GitHub Actions workflows reference these secrets/variables
3. The Pulumi action uses `config-map` to pass values to stacks
4. Pulumi YAML files reference these configs using `${variable_name}`

**Example `Pulumi.yaml`:**
```yaml
name: ecs-core-api
runtime: yaml
packages:
  service: https://github.com/mManagedKube/devops-with-ai.git/pulumi/components/aws/ecs/service@0.0.11

configuration:
  llm_name:
    type: String
  api_sentry_dsn:
    type: String

resources:
  coreApiService:
    type: service:index:Service
    properties:
      environment:
        - name: LLM_NAME
          value: ${llm_name}
        - name: API_SENTRY_DSN
          value: ${api_sentry_dsn}
```

**Example GitHub Action Configuration:**
```yaml
- name: Pulumi Preview
  uses: pulumi/actions@v6
  with:
    command: preview
    config-map: |
      {
        "api_alb_cert_arn": {"value": "${{ vars.PROD_API_ALB_CERT_ARN }}", "secret": true},
        "api_sentry_dsn": {"value": "${{ secrets.PROD_API_SENTRY_DSN }}", "secret": true},
        "llm_name": {"value": "${{ vars.PROD_LLM_NAME }}", "secret": false}
      }
```

**Note:** We don't use `pulumi config set` locally to keep all configuration centralized in GitHub Actions.

## Destroying Infrastructure via GitHub Actions

To destroy infrastructure stacks using GitHub Actions:

1. **Create a new branch** for the destroy operation

2. **Modify the workflow** (e.g., `pulumi_prod.yaml` or `pulumi_staging.yaml`):
   - Change `command: preview` to `command: destroy`

3. **Push to PR**: The destroy will run in the pull request

4. **Important**: 
   - Usually **DO NOT merge** destroy PRs
   - If you do merge, change the command back to `preview` first
   - This prevents future PRs from accidentally destroying infrastructure

**Use Case**: When you need to tear down a specific stack (RDS, ECS, etc.) without setting up Pulumi locally.