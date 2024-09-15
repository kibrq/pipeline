from typing import Optional, Union, Dict, List
from pathlib import Path

import pipeline

ShellArguments = pipeline.get_class('shell_templates.Arguments')
ShellCommand = pipeline.get_class('shell_templates.Command')
ShellCommandConfigurator = pipeline.get_class('shell_templates.Configurator')

from dataclasses import dataclass, field, fields, asdict
from string import Template
from copy import deepcopy


def deep_set_default(d: dict, default_values: dict):
    """
    Recursively sets default values for missing or None keys in a nested dictionary.
    
    :param d: The target dictionary to update.
    :param default_values: The default values dictionary to use.
    """
    for key, default in default_values.items():
        # If key is missing or is None, set it to the default value
        if key not in d or d[key] is None:
            d[key] = default
        # If both are dictionaries, recurse into the nested dictionary
        elif isinstance(d[key], dict) and isinstance(default, dict):
            deep_set_default(d[key], default)


def update_dataclass(one, another, dtype=None):
    data = asdict(one)
    deep_set_default(data, asdict(another))
    
    if dtype is None: dtype = type(one)
    def dataclass_from_dict(dtype, data):
        try:
            fieldtypes = { f.name: f.type for f in fields(dtype)}
            return dtype(**{f: dataclass_from_dict(fieldtypes[f], data[f]) for f in data})
        except BaseException as ex:
            return data # Not a dataclass field
    return dataclass_from_dict(dtype, data)


@dataclass
class SlurmSBatchHeader:
    
    mem: Optional[str] = None

    mem_per_cpu: Optional[str] = None

    ntasks: Optional[int] = None

    output: Optional[str] = None

    output_template: Optional[str] = None

    error: Optional[str] = None

    error_template: Optional[str] = None

    array: Optional[str] = None

    array_template: Optional[str] = None

    reservation: Optional[str] = None

    time: Optional[str] = None

    job_name: Optional[str] = None

    job_name_template: Optional[str] = None

    cpus_per_task: Optional[int] = None

    #...
    
    def to_sbatch_header_string(self, metadata={}):
        data = asdict(self)

        for k, v in data.items():
            if k.endswith('template'):
                continue
            if not f'{k}_template' in data:
                continue
            if data[f'{k}_template'] is None:
                continue
            if v:
                continue
            data[k] = data[f'{k}_template'].format(**metadata)
        
        return '\n'.join([
            f"#SBATCH --{key.replace('_', '-')}={value}"
            for key, value in data.items() if not value is None and not key.endswith('template')
        ])


@dataclass
class SlurmDefaultTemplateBody:
    before_command: Optional[str] = None

    exec: Optional[str] = None

    after_command: Optional[str] = None


@dataclass
class Slurm:
    template: Optional[str] = None

    header: SlurmSBatchHeader = field(default_factory=SlurmSBatchHeader)

    body: SlurmDefaultTemplateBody = field(default_factory=SlurmDefaultTemplateBody)

    filename_template: Optional[str] = None


@dataclass
class SlurmCommand(ShellCommand):
    slurm: Slurm = field(default_factory=Slurm)

    def build(self, *args, __factory=None, **kwargs):
        if __factory is None:
            __factory = SlurmCommandConfigurator
        
        return super().build(*args, __factory=__factory, **kwargs)


@dataclass
class SlurmArguments(ShellArguments):
    default_slurm: Slurm = field(default_factory=lambda: Slurm())

    folders_to_create: List[str] = field(default_factory=lambda: ['logs'])

    def __post_init__(self):
        getattr(super(), '__post_init__')()

        for folder in self.folders_to_create:
            (self.build_path / folder).mkdir(parents=True, exist_ok=True)

        self.default_slurm = update_dataclass(self.default_slurm, Slurm(
        template =\
"""#!/bin/bash

${header}

${before_command}

# Take SLURM_ARRAY_TASK_ID line from .sh script
command=$$(cat ${build_path}/$${SLURM_JOB_NAME}.sh | sed -n "$${SLURM_ARRAY_TASK_ID}p")

echo "Executing $${command}"
echo "Started at $$(date)"

${exec} $${command}

echo "Finished at $$(date)"

${after_command}
""",
        header = SlurmSBatchHeader(
            job_name_template = '{name}',
            output_template = '{build_path}/logs/stdout_{name}_%a.log',
            error_template = '{build_path}/logs/stderr_{name}_%a.log',
            array_template = '1-{array_size}'
        ),
        
        body = SlurmDefaultTemplateBody(
            before_command = '',
            after_command = '',
            exec = 'eval',    
        ),
        
        filename_template = '{build_path}/slurm_{name}.sh',  
        ))
        

        for f in fields(self):
            if (command := getattr(self, f.name)) and isinstance(command, SlurmCommand):
                setattr(command, 'slurm', update_dataclass(getattr(command, 'slurm'), self.default_slurm))


@dataclass
class SlurmCommandConfigurator(ShellCommandConfigurator):
    __slurm_array_size: int = 0

    slurm_template: Optional[str] = None

    slurm_header: SlurmSBatchHeader = field(default_factory=SlurmSBatchHeader)

    slurm_body: Dict[str, str] = field(default_factory=lambda: {})
    
    slurm_filename_template: Optional[str] = None 

    def __post_init__(self):
        getattr(super(), '__post_init__')()
        
        assert self.args
        assert self.name    

    
    def append_command(self, *args, **kwargs):
        self.__slurm_array_size += 1
        getattr(super(), 'append_command')(*args, **kwargs)

    
    @property
    def metadata(self):
        data = getattr(super(), 'metadata')
        return {
            **data,
            'array_size': self.__slurm_array_size,
        }


    def slurm_finalize(
        self,
    ):
        template = self.slurm_template
        filename_template = self.slurm_filename_template
        header = self.slurm_header
        mapping = self.slurm_body

        if hasattr(self.command, 'slurm'):
            if template is None:
                template = self.command.slurm.template
            if filename_template is None:
                filename_template = self.command.slurm.filename_template
            for k, v in asdict(self.command.slurm.body).items():
                mapping.setdefault(k, v)
            header = update_dataclass(header, self.command.slurm.header)

        mapping.setdefault('header', header.to_sbatch_header_string(self.metadata))
        for k, v in self.metadata.items():
            mapping.setdefault(k, v)

        with open(filename_template.format(**self.metadata), 'w') as file:
            file.write(Template(template).substitute(mapping))
            
    
    def __exit__(self, *args, **kwargs):
        self.slurm_finalize()
        return super().__exit__(*args, **kwargs)
