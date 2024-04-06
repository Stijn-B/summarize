from dataclasses import dataclass
from pathlib import Path
import os
import argparse
from typing import Any, Callable, List, Union
import tiktoken

model = "gpt-3.5-turbo"  # "gpt-4"

enc = tiktoken.encoding_for_model(model)

# SETTIGNS

suffix_to_language = {
    ".js": "javascript",
    ".css": "css",
    ".html": "html",
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
}

filetypes_to_include = suffix_to_language.keys()

# UTILS


def remove_imports(text: str) -> str:
    result = []
    for line in text.split("\n"):
        if not (line.startswith("import") or line.startswith("from")):
            result.append(line)
    return "\n".join(result)



# FILTERS

def global_filter(file: Path, filetypes_to_include: List[str] = filetypes_to_include, filter_dotfiles: bool = True, filter_tests: bool = False, **kwargs) -> bool:
    """
    Returns wether a file is filtered out (excluded from the summary).
    """

    FILTERS: List[bool] = [
        filter_dotfiles and file.name.startswith("."),
        filter_tests and (file.name.startswith("test") and file.name.startswith("__tests__")),
        # Django
        file.name.startswith("migrations"),
        file.name.startswith("admin"),
        file.name.startswith("apps"),
        # Next.js

    ]
    if any(FILTERS):
        return True
    
    FILE_FILTERS: List[bool] = [
        file.suffix not in filetypes_to_include,
        # Python
        file.name.startswith("__init__"),
    ]
    if file.is_file() and any(FILE_FILTERS):
        return True
    
    DIR_FILTERS: List[bool] = [
        # Python
        "venv" in str(file.name),
        # Django
        "management/commands" in str(file),
        "htmlcov" in str(file.name),
        "dist" in str(file.name),
        # Node
        "node_modules" in str(file.name),
    ]
    if file.is_dir() and any(DIR_FILTERS):
        return True
    

    return False

# SUMMARIZE

@dataclass
class Summary: 
    summaries: List[str]

    @property
    def text(self) -> str:
        return "\n\n".join(self.summaries)
    
    @property
    def file_names(self) -> List[str]:
        return [summary.split("\n")[0].strip("## ") for summary in self.summaries]
    
    def print(self, detailed: bool, **kwargs):
        text = self.text + "\n"
        for summary, file_name in zip(self.summaries, self.file_names):
            text += f"\n"
            if detailed:
                text += f"{len(enc.encode(summary))} "
            text += file_name
        text += "\n\ntokens: " + str(len(enc.encode(text)))
        return text


    def __str__(self) -> str:
        token_count = len(enc.encode(self.text))
        return self.text + "\n\nFiles:" + '\n'.join(self.file_names) + f"\n\nTokens: {token_count}"

    def __add__(self, other: "Summary") -> "Summary":
        return Summary(
            summaries=self.summaries + other.summaries
        )

    def __len__(self) -> int:
        return len(self.summaries)

    def __bool__(self) -> bool:
        return bool(self.summaries)

def summarize(
        folder: Union[Path, str], 
        filters: List[Callable[[Path, dict[str, Any]], bool]] = [],
        **kwargs
    ) -> Summary:

    summary = Summary([])
    for file in Path(folder).iterdir():

        # check if file should be filtered out
        if any([filter(file, **kwargs) for filter in filters]):
            continue

        # recursively summarize directories
        if file.is_dir() and (directory_summary := summarize(file, filters, **kwargs)):
            summary += directory_summary
        
        # summarize files
        else:  
            if file.suffix in filetypes_to_include:
                file_text = file.read_text()
                file_text = remove_imports(file_text).strip("\n").strip()
                summary += Summary([(
                    f"## {file}\n```{suffix_to_language.get(file.suffix, file.suffix)}\n{file_text}\n```"
                )])
                token_count = len(enc.encode(summary.text))

                

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--folder', type=str, help='folder contents to summarize')
    parser.add_argument('--hide_file_list', default=False, action="store_true", help='don\'t output the file list')
    parser.add_argument('--detailed', default=True, action="store_true", help='add token counts to the file list')
    parser.add_argument('--filter_tests', default=False, action="store_true", help='exclude test files')
    parser.add_argument('--filter_dotfiles', default=True, action="store_true", help='ignore both .file and .directory')
    args = parser.parse_args()

    kwargs = vars(args)
    summary = summarize(
        **kwargs,
        filters=[global_filter]
    )
    
    print(summary.print(**kwargs))