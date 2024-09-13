from setuptools import setup, find_packages

setup(
    name='pipeline-shell-templates-plugin',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'pipeline.plugins': [
            'MyPlugin = shell_templates.shell_templates:ShellTemplatesArguments'
        ]
    },
    install_requires=[
        'pipeline @ git+https://github.com/kibrq/pipeline.git'
    ],
)
