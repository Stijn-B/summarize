from pathlib import Path
from typing import List, Optional, Union

from tiktoken import Encoding

from settings import SUFFIX_TO_LANGUAGE


def read_files(files: Union[Path, List[Path]], folder: Optional[Path] = None) -> str:
    if not isinstance(files, list):
        files = [files]
    assert all(file.is_file() for file in files), f"`files` must be all files"
    
    files_texts = []
    for file in files:
        file_name = file.relative_to(folder) if folder else file
        file_content = "ERROR READING THIS FILE"
        try:
            file_content = file.read_text().strip()
        except Exception as e:
            print(f"Error reading {file_name}: {e}")
            continue
        files_texts.append(f"## {file_name}\n```{SUFFIX_TO_LANGUAGE.get(file.suffix, file.suffix)}\n{file_content}\n```")
    return "\n\n".join(files_texts)


def directory_outline_full(files: List[Path], folder: Path, enc: Encoding) -> str:
    individual_file_token_counts = [len(enc.encode(read_files(file))) for file in files]
    max_token_count_digits = len(str(max(individual_file_token_counts)))

    info = ""
    for i, (token_count, file) in enumerate(zip(individual_file_token_counts, files)):
        token_count_str = str(token_count).ljust(max_token_count_digits)
        clean_name = file.relative_to(folder)
        info += f"{clean_name} ({token_count_str.strip()})\n"
    return info


def directory_outline_pretty(files: List[Path], folder: Path, enc) -> str:
    def print_files(path: Path, file_list: List[Path], prefix: str = ""):
        lines = []
        contents = sorted(path.iterdir())
        for i, item in enumerate(contents):
            is_last = i == len(contents) - 1
            if item in file_list:
                with open(item, "r") as f:
                    count = len(enc.encode(f.read()))
                lines.append(
                    f"{prefix}{'└── ' if is_last else '├── '}{item.name} ({count})"
                )
            if item.is_dir():
                new_prefix = prefix + ("    " if is_last else "│   ")
                lines.extend(print_files(item, file_list, new_prefix))
        return lines

    lines = ["."]
    lines.extend(print_files(folder, files))
    return "\n".join(lines)


def directory_outline_compact(files: List[Path], folder: Path, enc: Encoding) -> str:
    def print_files(path: Path, file_list: List[Path], prefix: str = ""):
        lines = []
        contents = sorted(path.iterdir())
        for i, item in enumerate(contents):
            if item in file_list:
                with open(item, "r") as f:
                    count = len(enc.encode(f.read()))
                lines.append(f"{prefix}- {item.name} ({count})")
            if item.is_dir():
                new_prefix = prefix + "  "
                lines.extend(print_files(item, file_list, new_prefix))
        return lines

    lines = []
    lines.extend(print_files(folder, files))
    return "\n".join(lines)
