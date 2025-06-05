# pulp-manifest

A tool for the Pulp File plugin to generate a PULP_MANIFEST so the directory can be recognized by Pulp.

For more information about File plugin, see [its documentation](https://docs.pulpproject.org/pulp_file/).

## Usage

To generate a PULP_MANIFEST for a local directory, run:

```
pulp-manifest /path/to/directory/for/which/manifest/needs/to/be/created
```

To generate a PULP_MANIFEST for an S3 bucket path, use:

```
pulp-manifest s3://bucket-name/path/to/prefix/
```

You can also exclude files or directories matching a glob pattern using the `--filter` option:

```
pulp-manifest /path/to/directory --filter '*.tmp'
pulp-manifest s3://bucket-name/path --filter '*.log'
```

This will exclude files or directories matching the given pattern from the generated manifest.