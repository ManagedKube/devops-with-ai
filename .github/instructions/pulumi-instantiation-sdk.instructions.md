---
applyTo: "pulumi/environments/**/sdks/*/*.yaml"
---
The sdk folder holds the Pulumi package information.  A package is a pulumi component reference
either by a relative path or a git URL and a tagged version.

There can ONLY BE ONE yaml file in each of these sdk sub folders.  If there are more than one file,
in the last folder it can cause problems.  When adding or modifying Pulumi the pulumi instantiation sdk files in this directory, make sure there is only one yaml file in each sdk sub folder.
