from typing import List, Callable, Union
from pathlib import Path


class FileSelector:
    """
    A class for selecting and filtering files based on the given criteria.
    """

    def __init__(self, filetypes_to_include: List[str], filter_dotfiles: bool, filter_tests: bool):
        """
        Initializes a FileSelector object with the given parameters.

        Args:
            filetypes_to_include (List[str]): A list of file extensions to include in the selection.
            filter_dotfiles (bool): Whether to exclude files and directories starting with a dot.
            filter_tests (bool): Whether to exclude test files.
        """
        self.filetypes_to_include = filetypes_to_include
        self.filter_dotfiles = filter_dotfiles
        self.filter_tests = filter_tests

    def global_filter(self, file: Path) -> bool:
        """
        Returns whether a file should be filtered out (excluded from the summary).

        Args:
            file (Path): The file to check.

        Returns:
            bool: True if the file should be filtered out, False otherwise.
        """
        FILTERS: List[bool] = [
            self.filter_dotfiles and file.name.startswith("."),
            self.filter_tests and (file.name.startswith("test") or file.name.startswith("__tests__")),
        ]
        if any(FILTERS):
            return True

        FILE_FILTERS: List[bool] = [
            file.suffix not in self.filetypes_to_include,
        ]
        if file.is_file() and any(FILE_FILTERS):
            return True

        DIR_FILTERS: List[bool] = []
        if file.is_dir() and any(DIR_FILTERS):
            return True

        return False

    def select_files(self, folder: Union[Path, str], filters: List[Callable[[Path], bool]]) -> List[Path]:
        """
        Selects files from the given folder based on the given filters.

        Args:
            folder (Union[Path, str]): The folder to select files from.
            filters (List[Callable[[Path], bool]]): A list of filters to apply to the files.

        Returns:
            List[Path]: A list of selected files.
        """
        selected_files = []
        for file in Path(folder).iterdir():
            if self.global_filter(file) or any(filter(file) for filter in filters):
                continue
            if file.is_dir():
                selected_files.extend(self.select_files(file, filters))
            elif file.suffix in self.filetypes_to_include:
                selected_files.append(file)
        return selected_files


def filter_by_filetype(file: Path, filetypes_to_include: List[str]) -> bool:
    """
    Returns whether a file should be filtered out based on its file type.

    Args:
        file (Path): The file to check.
        filetypes_to_include (List[str]): A list of file extensions to include.

    Returns:
        bool: True if the file should be filtered out, False otherwise.
    """
    return file.suffix not in filetypes_to_include


def filter_by_dotfile(file: Path) -> bool:
    """
    Returns whether a file should be filtered out based on whether it starts with a dot.

    Args:
        file (Path): The file to check.

    Returns:
        bool: True if the file should be filtered out, False otherwise.
    """
    return file.name.startswith(".")


def filter_by_tests(file: Path) -> bool:
    """
    Returns whether a file should be filtered out based on whether it is a test file.

    Args:
        file (Path): The file to check.

    Returns:
        bool: True if the file should be filtered out, False otherwise.
    """
    return file.name.startswith("test") or file.name.startswith("__tests__")