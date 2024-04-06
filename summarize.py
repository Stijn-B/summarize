
from pathlib import Path
import argparse
from file_printing import read_files
from file_selection import filter_files, global_filter, python_files_only, select_files
import tiktoken


model = "gpt-3.5-turbo"  # "gpt-4"

enc = tiktoken.encoding_for_model(model)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--folder', type=str, required=True, help='folder contents to summarize')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--exclude_indices', nargs='*', type=int, default=[], help='list of file indices to exclude from the summary, cannot be combined with include_indices')
    group.add_argument('--include_indices', nargs='*', type=int, default=[], help='list of file indices to include in the summary, cannot be combined with exclude_indices')
    parser.add_argument('--hide_file_list', default=False, action="store_true", help='don\'t output the file list')
    parser.add_argument('--detailed', default=True, action="store_true", help='add token counts to the file list')
    parser.add_argument('--exclude_files', nargs='*', type=str, default=[], help='list of file/folder paths to exclude from the summary')
    parser.add_argument('--filter_tests', default=False, action="store_true", help='exclude test files')
    parser.add_argument('--filter_dotfiles', default=True, action="store_true", help='ignore both .file and .directory/')
    parser.add_argument('--embeddings_selection', default=False, action="store_true", help='add token counts to the file list')
    parser.add_argument('--python_only', default=False, action="store_true", help='only include python files')
    parser.add_argument('--task_instruction', default="", help='text that is added to the "Task" section.')
    args = parser.parse_args()
    kwargs = vars(args)
    args.exclude_files = [Path(p) for p in args.exclude_files]
    folder = Path(args.folder)

    # file and folder filters

    # select files
    all_files, _ = select_files(
        Path(folder), 
        filters=[global_filter],
        **kwargs
    )
    
    # optional filters
    filters = []
    if args.filter_tests:
        filters.append(lambda file, **kwargs: not "test" in str(file).lower())
    if args.filter_dotfiles:
        filters.append(lambda file, **kwargs: not file.name.startswith("."))
    if args.python_only:
        filters.append(python_files_only)
    if args.exclude_files:
        exclude_filter = filter_files(Path(folder), args.exclude_files)
        filters.append(exclude_filter)
    files = [file for file in all_files if 
             all([filter(file, **kwargs) for filter in filters])
             or file.name == "Pipfile"
             ]


    if len(all_files) == 0:
        print("NO FILES FOUND")
        exit()



    # the files to print out in the summary can depend on exclude_indices or include_indices
    if args.include_indices:
        files_to_include = [file for i, file in enumerate(files) if i in args.include_indices]
    else:
        files_to_include = [file for i, file in enumerate(files) if i not in args.exclude_indices]
    files_text = read_files(files_to_include, folder)

    # token counts
    individual_file_token_counts = [len(enc.encode(read_files(file))) for file in files]
    total_token_count = len(enc.encode(files_text))

    # prepare zfill and ljust arguments
    max_index_digits = len(str(len(files)))
    max_token_count_digits = len(str(max(individual_file_token_counts)))
    
    # print summary
    output_string = f"# Open Files (relative to {folder})\n\n"
    output_string += files_text
    output_string += "\n"
    output_string += "\n\n# Folder Layout\n"
    output_string += "".join(["\n" + str(file.relative_to(folder)) for file in all_files])
    output_string += f"\n\n# Task\n\n{args.task_instruction}\n\n\n\n"

    info = ""
    info += "\ni".ljust(max_index_digits) + " [x] " + "tokens".ljust(max_token_count_digits) + " file"
    for i, (token_count, file) in enumerate(zip(individual_file_token_counts, files)):
        token_count_str = str(token_count).ljust(max_token_count_digits)
        checkbox = "[x]" if file in files_to_include else "[ ]"
        clean_name = str(file)[len(str(folder))+1:] if str(folder) == str(file)[:len(str(folder))] else str(file)
        info += f"\n{str(i).zfill(max_index_digits)} {checkbox} {token_count_str} {clean_name}"
    info += "\n"
    info += f"\ntotal tokens: {total_token_count}"
    info += "\n"
    info += "\nfilters:"
    for filter in filters:
        info += f"\n  {filter.__name__}"


    print("".join(["\n" + str(file.relative_to(folder)) for file in all_files]))
    print(info)


    # write summary to file
    (folder / "summary.txt").write_text(output_string)





