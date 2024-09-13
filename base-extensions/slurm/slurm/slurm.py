from typing import Optional, Union, Dict
from pathlib import Path

import pipeline

ShellCommand = pipeline.get_class('shell_templates.Command')
ShellCommandConfigurator = pipeline.get_class('shell_templates.Configurator')

from dataclasses import dataclass, field, fields, asdict
from string import Template
from copy import deepcopy


@dataclass
class SlurmSBatchHeader:
    
    mem: Optional[str] = None

    mem_per_cpu: Optional[str] = None

    ntasks: Optional[int] = None

    output: Optional[str] = None

    error: Optional[str] = None

    array: Optional[str] = None

    reservation: Optional[str] = None

    time: Optional[str] = None

    #...

    def update(self, other, dtype=None):
        if dtype is None:
            dtype = type(self)

        arguments = dtype()
        
        for f in fields(type(other)) + fields(type(self)):
            if hasattr(self, f.name) and not getattr(self, f.name) is None:
                setattr(arguments, f.name, getattr(self, f.name))
                continue
            if hasattr(other, f.name) and not getattr(other, f.name) is None:
                setattr(arguments, f.name, getattr(other, f.name))

        return arguments

    def to_sbatch_header_string(self):
        return '\n'.join([
            f"#SBATCH --{key.replace('_', '-')}={value}"
            for key, value in asdict(self).items() if not value is None
        ])


@dataclass
class SlurmCommandConfiguratorFactory:
    template: Union[str, Path] = \
"""
#! /bin/bash/

${header}

BUILD_PATH=${build_path}
${before_command}

# Take SLURM_ARRAY_TASK_ID line from .sh script
command=$$($${BUILD_PATH}/$${SLURM_JOB_NAME}.sh | sed -n "$${SLURM_ARRAY_TASK_ID}p")

echo "Executing $${command}"
echo "Started at $$(date)"

${exec} $${command}

echo "Finished at $$(date)"

${after_command}
"""

    prefix: str = 'slurm_'
    
    header: SlurmSBatchHeader = field(default_factory=SlurmSBatchHeader)

    template_arguments: Dict[str, str] = field(default_factory=lambda: {
        "before_command": "",
        "exec": "eval",
        "after_command": "",
    })

    def build(self, *args, **kwargs):
        return SlurmCommandConfigurator(
            *args, **kwargs,
            slurm_prefix = self.prefix,
            slurm_header = self.header,
            slurm_template = self.template,
            slurm_template_arguments = self.template_arguments,
        )


SLURM_DEFAULT = SlurmCommandConfiguratorFactory()


@dataclass
class SlurmCommand(ShellCommand):
    slurm: SlurmSBatchHeader = field(default_factory=SlurmSBatchHeader)

    slurm_template: Union[str, Path] = None

    slurm_template_arguments: Dict[str, str] = field(default_factory=lambda: {})

    def build(self, __factory=SLURM_DEFAULT.build, **kwargs):
        return super().build(**kwargs, __factory=__factory)



@dataclass
class SlurmCommandConfigurator(ShellCommandConfigurator):
    slurm_prefix: str = 'slurm_'

    slurm_header: SlurmSBatchHeader = field(default_factory=SlurmSBatchHeader)

    slurm_template: Union[str, Path] = None

    slurm_template_arguments: Dict[str, str] = field(default_factory=lambda: {})

    _array_count: int = 0

    
    def append_command(self, *args, **kwargs):
        self._array_count += 1
        getattr(super(), 'append_command')(*args, **kwargs)

    
    def slurm_finalize(
        self,
        filename: Optional[str] = None,
        filepath: Optional[str] = None,
        template: Optional[Union[str, Path]] = None,
        header: Optional[SlurmSBatchHeader] = None,
        template_arguments: Dict[str, str] = None,
    ):

        filepath = getattr(super(), 'resolve_paths')(filepath=filepath, filename=filename)
        
        if template is None:
            if hasattr(self.command, 'slurm_template') and not self.command.slurm_template is None:
                template = self.command.slurm_template
            else:
                template = self.slurm_template

        if header is None:
            header = SlurmSBatchHeader()

        if hasattr(self.command, 'slurm'):
            header = header.update(self.command.slurm)

        header = header.update(self.slurm_header)
        header = header.update(SlurmSBatchHeader(array=f"1-{self._array_count}"))
        
        if template_arguments is None:
            template_arguments = deepcopy(self.slurm_template_arguments)

        else:
            template_arguments.update(self.slurm_template_arguments)

        if not 'header' in template_arguments:
            template_arguments['header'] = header.to_sbatch_header_string()

        if not 'build_path' in template_arguments:
            template_arguments['build_path'] = self.args.build_path

        if isinstance(template, Path):
            template = template.read_text()

        with open(filepath.parents[0] / f'{self.slurm_prefix}{filepath.name}', 'w') as file:
            file.write(Template(template).substitute(template_arguments))

    
    def __exit__(self, *args, **kwargs):
        self.slurm_finalize()
        return super().__exit__(*args, **kwargs)