from setuptools import setup, find_packages

setup(
    name='pipeline-shell-templates-plugin',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'pipeline.plugins': [
            'shell_templates.Command = shell_templates.shell_templates:ShellTemplatesCommand',
            'shell_templates.Arguments = shell_templates.shell_templates:ShellTemplatesArguments',
            'shell_templates.Configurator = shell_templates.shell_templates:ShellTemplatesCommandConfigurator'
        ]
    },
    install_requires=[
        'pipeline @ git+ssh://git@github.com/kibrq/pipeline.git'
    ],
)
