from pathlib import Path
from typing import List, Callable, Any, Dict, Union

from settings import FILTER_DOTFILES, FILTER_TESTS, FILETYPES_TO_INCLUDE


def global_filter(
    file: Path,
    filetypes_to_include: List[str] = FILETYPES_TO_INCLUDE,
    filter_dotfiles: bool = FILTER_DOTFILES,
    filter_tests: bool = FILTER_TESTS,
    **kwargs
) -> bool:
    """
    Returns wether a file is passes the filter.
    """

    FILTERS: List[bool] = [
        not (filter_dotfiles and file.name.startswith(".")),
        not (filter_tests
            and (file.name.startswith("test") and file.name.startswith("__tests__"))
        ),
        # Django
        not file.name.startswith("migrations"),
        not file.name.startswith("admin"),
        #not file.name.startswith("apps"),
    ]
    if not all(FILTERS):
        return False
    
    if file.is_file():
        FILE_FILTERS: List[bool] = [
            file.suffix in filetypes_to_include,
            # Python
            not file.name.startswith("__init__"),
        ]
        if not all(FILE_FILTERS):
            return False

    if file.is_dir():
        DIR_FILTERS: List[bool] = [
            # Python
            "venv" not in str(file.name),
            # Django
            "htmlcov" not in str(file.name),
            "dist" not in str(file.name),
            # Node
            "node_modules" not in str(file.name),
            # ElderJs
            "___ELDER___" not in str(file.name),
        ]
        if not all(DIR_FILTERS):
            return False
            

    return True



def filter_files(working_dir: Path, files_and_folders: List[Path]) -> Callable[[Path, Dict[str, Any]], bool]:
    abs_files_and_folders = [p.resolve() if p.is_absolute() else (working_dir / p).resolve() for p in files_and_folders]
    def _exclude_files(file: Path, **kwargs) -> bool:
        return not any([bool(parent in abs_files_and_folders) for parent in file.parents])
    return _exclude_files


def python_files_only(file: Path, **kwargs) -> bool:
    return file.is_dir() or file.suffix == ".py"


def select_files(
    files_and_folders: Union[Path, List[Path]],
    filters: List[Callable[[Path, Dict[str, Any]], bool]] = [global_filter],
    **filter_kwargs: Dict[str, Any]
) -> List[List[Path]]:

    selected_files, all_files = [], []
    
    def _select_files(path: Path, select: bool = True):
        select = select and all([filter(path, **filter_kwargs) for filter in filters])
        
        # recursively collect files
        if path.is_file():
            if select:
                selected_files.append(path)
            all_files.append(path)
        elif path.is_dir():
            for child in path.iterdir():
                _select_files(child, select)
    
    for item in files_and_folders if isinstance(files_and_folders, list) else [files_and_folders]:
        _select_files(item)
    selected_files.sort()
    all_files.sort()
    return selected_files, all_files
