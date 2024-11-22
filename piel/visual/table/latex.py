# Function to escape LaTeX special characters
def escape_latex(s: str) -> str:
    replacements = {
        "&": r"&",
        "%": r"%",
        "$": r"$",
        "#": r"#",
        "_": r"_",
        "{": r"{",
        "}": r"}",
        "\\(": "",
        "\\)": "",
        "~": r"~",
        "^": r"^",
        "\\": "\\",
    }
    for original, replacement in replacements.items():
        s = s.replace(original, replacement)
    return s
