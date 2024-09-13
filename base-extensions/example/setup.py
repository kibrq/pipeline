from setuptools import setup, find_packages

setup(
    name='pipeline-exmample-plugin',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'pipeline.plugins': [
            'example.Command = example.example:MyCommand',
        ]
    },
    install_requires=[
        'pipeline-shell-templates-plugin @ git+ssh://git@github.com/kibrq/pipeline.git#egg=pipeline-shell-templates-plugin&subdirectory=base-extensions/shell-templates',
        'pipeline @ git+ssh://git@github.com/kibrq/pipeline.git'
    ],
)
