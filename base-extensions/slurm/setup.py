from setuptools import setup, find_packages

setup(
    name='pipeline-slurm-plugin',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'pipeline.plugins': [
            'slurm.Command = slurm.slurm:SlurmCommand',
            'slurm.Configurator = slurm.slurm:SlurmCommandConfigurator',
            'slurm.SBatchHeader = slurm.slurm:SlurmSBatchHeader',
            'slurm.CommandConfiguratorFactory = slurm.slurm:SlurmCommandConfiguratorFactory',
            'slurm.Default = slurm.slurm:SLURM_DEFAULT',
            
        ]
    },
    install_requires=[
        'pipeline-shell-templates-plugin @ git+ssh://git@github.com/kibrq/pipeline.git#egg=pipeline-shell-templates-plugin&subdirectory=base-extensions/shell-templates',
        'pipeline @ git+ssh://git@github.com/kibrq/pipeline.git'
    ],
)
