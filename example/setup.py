import pyrallis
import pipeline

BaseArguments = pipeline.get_class('slurm.Arguments')
Command = pipeline.get_class('slurm.Command')
DefaultBody = pipeline.get_class('slurm.DefaultTemplateBody')

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ParametrizedCommand(Command):
    some_parameter: int = 20 

@dataclass
class Arguments(BaseArguments):
    generate_file: Command = field(default_factory=Command)

    fill_file: ParametrizedCommand = field(default_factory=ParametrizedCommand)


@pyrallis.wrap()
def main(args: Arguments):

    with args.generate_file.build() as script:
        script.append_command()

    with args.fill_file.build() as script:
        script.append_command(mapping={
            'parameter': args.fill_file.some_parameter
        })


if __name__ == '__main__':
    main()

    