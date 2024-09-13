from typing import Optional, Union
from pathlib import Path

import pipeline

ShellCommand = pipeline.get_class('shell_templates.Command')
ShellCommandConfigurator = pipeline.get_class('shell_templates.CommandConfigurator')

from dataclasses import dataclass, field, fields, asdict


__SLURM_DEFAULT_TEMPLATE = """
#! /bin/bash/

${header}

BUILD_PATH=${build_path}
${before_command}

# Take SLURM_ARRAY_TASK_ID line from .sh script
command=$$($${BUILD_DIR}/$${SLURM_JOB_NAME}.sh | sed -n "$${SLURM_ARRAY_TASK_ID}p")

echo "Executing $${command}"
echo "Started at $$(date)"

${exec} $${command}

echo "Finished at $$(date)"

${after_command}
"""

__SLURM_DEFAULT_TEMPLATE_ARGUMENTS = {
    "before_command": "",
    "exec": "eval",
    "after_command": "",
}


@dataclass
class SlurmSBatchHeader:
    
    mem: Optional[str] = None

    mem_per_cpu: Optional[str] = None

    ntasks: Optional[int] = None

    output: Optional[str] = None

    error: Optional[str] = None

    array: Optional[str] = None

    #...

    def update(self: SlurmSBatchHeader, other: SlurmSBatchHeader, dtype=None):
        if dtype is None:
            dtype = type(self)

        arguments = dtype()
        
        for f in fields(type(other)) + fields(type(self)):
            if hasattr(self, f.name) and getattr(self, f.name) != None:
                setattr(arguments, f.name, getattr(self, f.name))
                continue
            if hasattr(other, f.name) and getattr(other, f.name) != None:
                setattr(arguments, f.name, getattr(other, f.name))

        return arguments

    def to_sbatch_header_string(self):
        return '\n'.join([f"#SBATCH --{key.replace('_', '-')}={value}" for key, value in asdict(self)])


@dataclass
class SlurmCommandConfiguratorFactory:
    prefix: str = 'slurm_'
    
    header: SlurmSBatchArguments = field(default_factory=SlurmSBatchArguments)

    template: Union[str, Path] = __SLURM_DEFAULT_TEMPLATE

    template_arguments: Dict[str, str] = field(default_factory=lambda: copy(__SLURM_DEFAULT_TEMPLATE_ARGUMENTS))

    def build(self, *args, **kwargs):
        return SlurmCommandConfigurator(
            *args, **kwargs,
            slurm_prefix = self.prefix,
            slurm_header = self.header,
            slurm_template = self.template,
        )


SLURM_DEFAULT = SlurmCommandConfiguratorFactory()


@dataclass
class SlurmCommand(ShellCommand):
    slurm: SlurmSBatchArguments = field(default_factory=lambda: SlurmSBatchArguments)

    slurm_template: Union[str, Path] = __SLURM_DEFAULT_TEMPLATE

    slurm_template_arguments: Dict[str, str] = field(default_factory=lambda: {})

    def build(self, **kwargs, __factory=SLURM_DEFAULT.build):
        return super().build(**kwargs, __factory=__factory)



@dataclass
class SlurmCommandConfigurator(ShellCommandConfigurator):
    slurm_prefix: str = 'slurm_'

    slurm_header: SlurmSBatchArguments = field(default_factory=SlurmSBatchArguments)

    slurm_template: Union[str, Path] = __SLURM_DEFAULT_TEMPLATE

    slurm_template_arguments: Dict[str, str] = field(default_factory=lambda: {})

    _array_count: int = 0

    
    def append_command(self, *args, **kwargs):
        self._array_count += 1
        super().append_command(*args, **kwargs)

    
    def slurm_finalize(
        self,
        filename: Optional[str] = None,
        filepath: Optional[str] = None,
        template: Optional[Union[str, Path]] = None,
        header: Optional[SlurmSBatchArguments] = None,
        template_arguments: Dict[str, str] = None,
    ):

        filepath = self.__resolve_paths(filepath=filepath, filename=filename)
        
        if template is None:
            if hasattr(self.command, 'slurm_template') and not self.command.slurm_template is None:
                template = self.command.slurm_template
            else:
                template = self.slurm_template

        if header is None:
            header = SlurmSBatchArguments()

        if hasattr(self.command, 'slurm'):
            header = header.update(self.command.slurm)

        header = header.update(self.slurm_header)
        header = header.update(SlurmSBatchArguments(array=f"1-{self._array_count}"))

        if template_arguments is None:
            template_arguments = self.slurm_template_arguments

        else:
            template_arguments.update(self.slurm_template_arguments)

        if not 'header' in template_arguments:
            template_arguments['header'] = header.to_sbatch_header_string()

        if isinstance(template, Path):
            template = template.read_text()

        with open(filepath.parents[0] / f'{self.slurm_prefix}{filepath.name}', 'w') as file:
            file.write(Template(template).substitute(template_arguments))

    
    def __exit__(self, *args, **kwargs):
        self.slurm_finalize()
        return super().__exit__(self, *args, **kwargs)