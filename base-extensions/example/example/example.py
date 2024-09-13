import pipeline

Command = pipeline.get_class('shell_templates.Command')

from dataclasses import dataclass

@dataclass
class MyCommand:
    my_parameter: str = 'hello world'
