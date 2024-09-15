from typing import List, Optional, Type
from pipeline.base import BaseArguments
from dataclasses import dataclass, field, fields
from string import Template
from pathlib import Path


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



@dataclass
class ShellTemplatesCommand:
    recipe: List[str] = field(default_factory=lambda: [])

    def build(self, **kwargs):
        if not 'args' in kwargs and hasattr(self, '__args'):
            kwargs['args'] = getattr(self, '__args')
        if not 'name' in kwargs and hasattr(self, '__name'):
            kwargs['name'] = getattr(self, '__name')
        if '__factory' in kwargs:
            __factory = kwargs.pop('__factory')
        else:
            __factory = ShellTemplatesCommandConfigurator

        return __factory(**kwargs)


@dataclass
class ShellTemplatesArguments(BaseArguments):

    def __post_init__(self):
        super().__post_init__()

        for f in fields(type(self)):
            if isinstance(getattr(self, f.name), ShellTemplatesCommand):
                setattr(getattr(self, f.name), '__args', self)
                setattr(getattr(self, f.name), '__name', f.name)


@dataclass
class ShellTemplatesCommandConfigurator:
    name: Optional[str] = None

    args: Optional[BaseArguments] = None

    filename_template: str = "{build_path}/{name}.sh"

    command: Optional[ShellTemplatesCommand] = None

    delimiter: str = ' '

    open_mode: str = 'w'

    recipe: List[str] = field(default_factory=lambda: [])
        
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.finalize()
        return False

    def __post_init__(self):
        if self.name is None and self.command is None:
            raise ValueError()

        if self.command is None and self.args is None:
            raise ValueError()
 
        if not self.args is None and self.command is None:
            self.command = getattr(self.args, self.name)

        assert isinstance(self.command, ShellTemplatesCommand)


    @property
    def metadata(self):
        return dict(
            name = self.name,
            build_path = None if self.args is None else str(self.args.build_path),
            # ...
        )

    def create_command(self, command=None, mapping=None, delimiter=None):
        if mapping is None:
            mapping = {}

        deep_set_default(mapping, self.metadata)

        if command is None:
            command = self.command

        if delimiter is None:
            delimiter = self.delimiter
        
        return delimiter.join([Template(part).substitute(mapping) for part in self.command.recipe])
        
    
    def append_command(
        self,
        command=None,
        command_str=None,
        mapping=None,
        delimiter=None,
    ):
        if command_str is None:
            command_str = self.create_command(mapping=mapping, delimiter=delimiter, command=command)

        self.recipe.append(command_str)

    
    def finalize(self):
        filename = self.filename_template.format(**self.metadata)

        with open(filename, self.open_mode) as file:
            file.write('\n'.join(self.recipe))
