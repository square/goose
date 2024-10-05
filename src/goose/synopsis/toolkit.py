# janky global state for now, think about it
from rich.rule import Rule
from attrs import define
from rich.markdown import Markdown
from pathlib import Path
from goose.toolkit.utils import get_language
import os
import platform
import json

from goose.toolkit.base import tool
from goose.toolkit.developer import Developer, RULESTYLE, RULEPREFIX
from goose.toolkit.utils import get_language

active_files = {}

def add_file(path: str, content: str, lang: str):
    active_files[path] = File(path, content, lang)


def remove_file(path: str):
    active_files.pop(path)


cwd = os.getcwd()

@define
class File:
    path: str
    content: str
    lang: str


def get_os():
    return json.dumps(dict(
        os=platform.system(),
        cwd=cwd,
        shell=os.environ.get('SHELL','unknown'),
    ), indent=4)


class SynopsisDeveloper(Developer):
    @tool
    def shell(self, command: str) -> str:
        """Execute a command on the shell

        This will return the output and error concatenated into a single string, as
        you would see from running on the command line. There will also be an indication
        of if the command succeeded or failed.

        Args:
            command (str): The shell command to run. It can support multiline statements
                if you need to run more than one at a time
        """
        if command.startswith("cat"):
            raise ValueError("You must read files through the read_file tool.")
        if command.startswith("cd"):
            raise ValueError("You must change dirs through the change_dir tool.")
        return super().shell(command)

    @tool
    def read_file(self, path: str) -> str:
        """Read the content of the file at path

        Args:
            path (str): The destination file path, in the format "path/to/file.txt"
        """
        language = get_language(path)
        content = Path(path).expanduser().read_text()
        self.notifier.log(Markdown(f"```\ncat {path}\n```"))
        # Record the last read timestamp
        self.timestamps[path] = os.path.getmtime(path)
        add_file(path=path, content=content, lang=language)

        return f"```{language}\n{content}\n```"

    @tool
    def write_file(self, path: str, content: str) -> str:
        """
        Write a file at the specified path with the provided content. This will create any directories if they do not exist.
        The content will fully overwrite the existing file.

        Args:
            path (str): The destination file path, in the format "path/to/file.txt"
            content (str): The raw file content.
        """  # noqa: E501
        language = get_language(Path(path))
        add_file(path=path, content=content, lang=language)
        return super().write_file(path, content)


    @tool
    def patch_file(self, path: str, before: str, after: str) -> str:
        """Patch the file at the specified by replacing before with after

        Before **must** be present exactly once in the file, so that it can safely
        be replaced with after.

        Args:
            path (str): The path to the file, in the format "path/to/file.txt"
            before (str): The content that will be replaced
            after (str): The content it will be replaced with
        """
        self.notifier.status(f"editing {path}")
        _path = Path(path)
        language = get_language(_path)

        content = _path.read_text()

        if content.count(before) > 1:
            raise ValueError("The before content is present multiple times in the file, be more specific.")
        if content.count(before) < 1:
            raise ValueError("The before content was not found in file, be careful that you recreate it exactly.")

        content = content.replace(before, after)
        add_file(path=path, content=content, lang=language)
        _path.write_text(content)

        output = f"""
```{language}
{before}
```
->
```{language}
{after}
```
"""
        self.notifier.log(Rule(RULEPREFIX + path, style=RULESTYLE, align="left"))
        self.notifier.log(Markdown(output))
        return "Succesfully replaced before with after."



    @tool
    def forget_file(self, path: str) -> str:
        """Forget about the file at the specified path

        Use this only when explicitly requested to.

        Args:
            path (str): The destination file path, in the format "path/to/file.txt"
        """
        global active_files
        remove_file(path)
        return "Completed"


    @tool
    def change_dir(self, path: str) -> str:
        """Change the directory to the specified path

        Args:
            path (str): The new dir path, in the format "path/to/dir"
        """
        global cwd
        cwd = path
        self.cwd = path
        return path
