import pyrallis
import pipeline

BaseArguments = pipeline.get_class('shell_templates.Arguments')
Command = pipeline.get_class('slurm.Command')
SLURM_DEFAULT = pipeline.get_class('slurm.Default')

from dataclasses import dataclass, field

@dataclass
class ParametrizedCommand(Command):
    some_parameter: int = 20

@dataclass
class Arguments(BaseArguments):
    generate_file: Command = field(default_factory=Command)

    fill_file: ParametrizedCommand = field(default_factory=ParametrizedCommand)


@pyrallis.wrap()
def main(args: Arguments):

    SLURM_DEFAULT.header.mem = "1gb"
    SLURM_DEFAULT.header.output = "stdout_%A_%a.log"
    SLURM_DEFAULT.header.error = "stderr_%A_%a.log"

    DEFAULT_VARIABLES = {
        'build_path': args.build_path,
    }
    
    with args.generate_file.build() as script:
        script.append_command(mapping={
            **DEFAULT_VARIABLES,
        })

    with args.fill_file.build() as script:
        script.append_command(mapping={
            **DEFAULT_VARIABLES,
            'parameter': args.fill_file.some_parameter
        })


if __name__ == '__main__':
    main()

    