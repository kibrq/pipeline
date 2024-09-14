from typing import Optional, List, Dict
from dataclasses import dataclass, field, asdict
from pathlib import Path, PosixPath
import yaml
from datetime import datetime


@dataclass
class BaseArguments:

    # The base directory path where build directories or configuration files will be stored.
    base_path: Path

    # Optional directory name inside base_path. If not provided, a unique directory name
    # will be generated based on the current date and time.
    build_dir: Optional[str] = None

    # Optional configuration file name that can be saved within the build_dir. If provided,
    # the full path to this config file will be created or checked.
    save_config_name: Optional[str] = None

    # Optional main script file name that can be saved within the build_dir. If provided,
    # the full path to this main script file will be created or checked.
    save_main_script_name: Optional[str] = None

    # If True, an existing config file will be overwritten. If False, an error will be raised
    # if the file already exists to prevent accidental overwrites.
    do_overwrite: bool = False

    # If True, the base directory and build directory will be created if they do not exist.
    # If False, the code will raise a FileNotFoundError if these directories do not exist.
    create_if_not_exist: bool = False

    @property
    def build_path(self):
        return self.base_path / self.build_dir

    @property
    def config_path(self):
        if self.save_config_name is None:
            return None
        return self.build_path / self.save_config_name

    @property
    def main_script_path(self):
        if self.save_main_script_name is None:
            return None
        return self.build_path / self.save_main_script_name

    
    def __post_init__(self):
        # Ensure base_path is a Path object, in case a string is provided
        if not isinstance(self.base_path, Path):
            self.base_path = Path(self.base_path)
        self.base_path = self.base_path.resolve()
        
        if not self.base_path.exists():
            if not self.create_if_not_exist:
                raise FileNotFoundError(f"Base path '{self.base_path}' does not exist and 'create_if_not_exist' is set to False.")
            else:
                # Create base_path if create_if_not_exist is True
                self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Generate a build directory name based on the current date and time if not provided
        if not self.build_dir:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.build_dir = f'build_{timestamp}'

        if not self.build_path.exists():
            if not self.create_if_not_exist:
                raise FileNotFoundError(f"Build directory '{self.build_path}' does not exist and 'create_if_not_exist' is set to `False`.")
            else:
                # Create build_dir if create_if_not_exist is True
                self.build_path.mkdir(parents=True, exist_ok=True)

        # Handle the overwrite logic
        if self.config_path and self.config_path.exists() and not self.do_overwrite:
            raise FileExistsError(f"{self.config_path} already exists. Set `do_overwrite=True` to overwrite it.")

        if self.config_path:
            with open(self.config_path, 'w') as file:
                yaml.dump(asdict(self), file)

        if self.main_script_path and self.main_script_path.exists() and not self.do_overwrite:
            raise FileExistsError(f"{self.main_script_path} already exists. Set `do_overwrite=True` to overwrite it.")

        if self.main_script_path:
            from shutil import copyfile
            from sys import argv
            
            copyfile(Path(argv[0]).resolve(), self.main_script_path)
        
    