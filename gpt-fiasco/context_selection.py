from typing import List

class ContextSelector:
    """
    Class for selecting the necessary files to answer a question using GPT-3.5.
    """
    
    def __init__(self, stub_files: List[str]):
        """
        Initializes the ContextSelector with a list of stub files.
        """
        pass
    
    def select_context(self, question: str, prompt: str) -> List[str]:
        """
        Selects the necessary files to answer a question using GPT-3.5.

        Pseudocode:
        1. Generate a list of all files that are not already in the stub files.
        2. Prompt the user with the given prompt and question using GPT-3.5.
        3. Parse the response to get a list of file names.
        4. Return the list of selected files, including the stub files and any additional files selected by the user.
        """
        pass
    
def parse_gpt_response(response: str) -> List[str]:
    """
    Parses the response from GPT-3.5 to get a list of selected file names.

    Pseudocode:
    1. Split the response into lines.
    2. Filter out any lines that do not start with a file name.
    3. Strip the file names of any leading or trailing whitespace.
    4. Return the list of selected file names.
    """
    pass