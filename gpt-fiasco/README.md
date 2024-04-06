OpenAI Logo
I'm writing a script that can summarize code projects. Here's the general goal:

1. select files to include in the summary (this functionality is covered by summarize.py)
2. add docstrings to all classes and functions (GPT-3.5)
3. generate type stubs with mypy
4. GPT("Here are the stubfiles of my project, please list the files of which you want the complete code to answer my question)
    → drastically cuts down the context size

```summarize.py
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
```

Here's an issue I made to document the requirements of the script:



# Code Project Summarization
## Summary

The code project summarization script should:

    Select files to include in the summary (see summarize.py): List[Path] -> List[Path]
    Add docstrings to all classes and functions using GPT-3.5: List[Path] -> List[dict[function or class, str]]
    Generate type stubs with mypy for Python code files: List[Path] code files -> List[Path] stub files
    List the files of which the complete code is needed to answer a question: List[Path] stub files, Question user question, Prompt -> GPT-3.5 -> selection List[Path] = Parse(GPT-Response)
    Combine the requested complete code files with stubbed out files to provide context for answering the questions: selection List[Path] + stub files of other files (not in selection) List[Path] -> summarize all of these

## Requirements

    GPT will determine which files to include in the summary. We give it all the stubbed files and ask "of which files would you like the complete code to be included to provide the necessary context for your answer?"
    Initially handle Python and JavaScript code. The script should be architected in such a way that more programming languages can be added later.
    The docstring should be in a standard appropriate for the programming language it's summarizing and should attempt to be concise because the context window is limited.
    Throw an exception if GPT-3.5 cannot generate a docstring for a class or function.
    Use mypy to generate type stubs for Python files. For JavaScript files, consider using TypeScript to generate type information. Further research is needed to determine the desired format.
    Throw an exception if mypy or TypeScript cannot generate type stubs for a file.
    Output just the file path for the list of files needed to answer a question.
    Throw an exception if the context size is still too large after summarization.
    No specific frameworks or libraries are required to be supported.
    The user provides a list of files and/or folders to include (these are then still filtered by the script like summarize.py already does now).