from typing import List, Optional, Type
from pipeline.base import BaseArguments
from dataclasses import dataclass, field, fields
from string import Template
from pathlib import Path


@dataclass
class ShellTemplatesCommand:
    parts: List[str] = field(default_factory=lambda: [])

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

    filename: Optional[str] = None

    filepath: Optional[Path] = None

    command: Optional[ShellTemplatesCommand] = None

    delimiter: str = ' '

    overwrite_if_exists: bool = True
        
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def __post_init__(self):
        if self.name is None and self.command is None:
            raise ValueError()

        if self.command is None and self.args is None:
            raise ValueError()
 
        if not self.args is None and self.command is None:
            self.command = getattr(self.args, self.name)

        assert isinstance(self.command, ShellTemplatesCommand)
        
        if self.filepath is None:

            assert not self.filename is None or not self.name is None

            if self.filename is None:
                self.filename = f'{self.name}.sh'

            self.filepath = self.args.build_path / self.filename

        if self.filepath and self.overwrite_if_exists:
            with open(self.filepath, 'w') as file:
                pass


    def resolve_paths(self, filename=None, filepath=None):
        if filepath is None:
            assert not self.filename is None or not filename is None
            if filename is None:
                filename = self.filename

            filepath = self.args.build_path / filename
        return filepath



    def create_command(self, command=None, mapping=None, delimiter=None):
        if mapping is None:
            mapping = {}

        if command is None:
            command = self.command

        if delimiter is None:
            delimiter = self.delimiter
        
        return delimiter.join([Template(part).substitute(mapping) for part in self.command.parts])

    
    def append_command(
        self,
        open_mode='a',
        filename=None,
        filepath=None,
        command=None,
        command_str=None,
        mapping=None,
        delimiter=None,
        add_newline: bool = True,
    ):
        filepath = self.resolve_paths(filepath=filepath, filename=filename)

        if command_str is None:
            command_str = self.create_command(mapping=mapping, delimiter=delimiter, command=command)

        with open(filepath, open_mode) as file:
            file.write(command_str)
            if add_newline:
                file.write('\n')
                

    