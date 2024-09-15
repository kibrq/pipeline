# Pipeline

This library (along with its plugins) allows to build *builds* of unbounded complexity.

## Plugins

This repo provides `base-extensions` as well. There you can find `shell-templates` a plugin allowing you to generate shell scripts by substituting placeholders
and `slurm` that adds SLURM support and allows you to generate SBATCH scripts alongside with shell-scripts to run this jobs on cluster.

To read an information about how to add new plugin please look into the `base-extensions/example` plugin

To load an existing plugin you just need to `pip install` it from `GitHub` or `pypi` (if it is stored there) and in your code you can use all of the defined objects in the plugin.

## Example

For example usage of `slurm` plugin please take a look into the `example`.

## Pyrallis
With [`pyrallis`](https://github.com/eladrich/pyrallis) you can add `YAML` configuration to your workflow. In the `example` folder you can see the how these two libraries can be combined.
