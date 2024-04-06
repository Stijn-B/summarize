SUFFIX_TO_LANGUAGE = {
    ".js": "javascript",
    ".css": "css",
    ".html": "html",
    ".svelte": "svelte",
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".md": "markdown",
    ".jinja": "jinja2",
    ".yml": "yaml",
    ".json": "json",
    "" : "",
    ".rst": "markdown",
    ".tf": "terraform",
    ".tfvars": "terraform",
    ".sh": "bash",
}

FILETYPES_TO_INCLUDE = SUFFIX_TO_LANGUAGE.keys()

# Filters

FILTER_DOTFILES = True
FILTER_TESTS = False