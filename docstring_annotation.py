import libcst as cst
from libcst.metadata import PositionProvider
from typing import List, Union
from pathlib import Path

def generate_function_docstring_with_gpt(node: cst.FunctionDef) -> str:
    # Implement your GPT-based docstring generator here
    return "This is a function docstring generated with GPT!"

def generate_class_docstring_with_gpt(node: cst.ClassDef) -> str:
    # Implement your GPT-based docstring generator here
    return "This is a class docstring generated with GPT!"

class DocstringTransformer(cst.CSTTransformer):
    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        if original_node.returns:
            first_statement = original_node.body.body[0] if original_node.body.body else None
            if not (isinstance(first_statement, cst.SimpleStatementLine) and isinstance(first_statement.body[0], cst.Expr) and isinstance(first_statement.body[0].value, cst.SimpleString)):
                docstring = generate_function_docstring_with_gpt(original_node)
                return updated_node.with_changes(body=cst.IndentedBlock([cst.SimpleStatementLine([cst.Expr(cst.SimpleString(f'"""{docstring}"""'))])].extend(updated_node.body.body)))
        return original_node

    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
        first_statement = original_node.body.body[0] if original_node.body.body else None
        if not (isinstance(first_statement, cst.SimpleStatementLine) and isinstance(first_statement.body[0], cst.Expr) and isinstance(first_statement.body[0].value, cst.SimpleString)):
            docstring = generate_class_docstring_with_gpt(original_node)
            return updated_node.with_changes(body=cst.IndentedBlock([cst.SimpleStatementLine([cst.Expr(cst.SimpleString(f'"""{docstring}"""'))])].extend(updated_node.body.body)))
        return original_node

def add_docstrings(file: Union[Path, List[Path]]) -> None:
    if isinstance(file, list):
        for path in file:
            add_docstrings(path)
        return

    assert file.is_file(), f"add_docstrings(): {file} is not a file"
    assert file.suffix == '.py', f"add_docstrings():{file} is not a Python file"
    
    source = file.read_text()
    tree = cst.parse_module(source)
    wrapper = cst.MetadataWrapper(tree)
    transformed_tree = wrapper.visit(DocstringTransformer())
    
    modified_source = transformed_tree.code
    file.write_text(modified_source)