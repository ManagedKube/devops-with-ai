---
applyTo: "pulumi/environments/**/Pulumi.yaml"
---
## What is this file
This is the Pulumi YAML file that defines the Pulumi stack configuration for this environment. It specifies the project name, runtime, and other settings needed to manage infrastructure as code using Pulumi.  It can use Pulumi components from this repository or from external sources.

## When the component version inside this file is modified
THE FOLLOWING MUST BE DONE AS PART OF THE PULL REQUEST MODIFYING THIS FILE's component version:

If the component is modified, in this example it is called packages.myComponent:
```yaml
name: my-stack
description: example stack
runtime: yaml
packages:
  myComponent: https://github.com/ManagedKube/devops-with-ai.git/pulumi/components/aws/myComponent@x.x.x
  # myComponent: ../../../../../components/aws/alb@0.0.0
```

If the `x.x.x` version is modified, then you must also update the corresponding file in the `sdks` 
subfolders to the same version number.

## When setting component reference to a local path
When asked to set the local component to a local path like:

```yaml
packages:
  myComponent: ../../../../../components/aws/myComponent@0.0.0
```

The AI agent should then run the following as a test to make sure it can add the pulumi component that was just created or modified:
1. change directory to the component's directory
1. run: python -m venv venv
1. run: source venv/bin/activate
1. run: pip install -r requirements.txt
1. Then change to the directory where the Pulumi.yaml file is that is using this local component
1. run: pulumi package add "to the path of the components directory in step 1"
1. The command in the previous step created a new file in the sdks folder.   Add this file to the PR.
1. Post your results back to the PR
