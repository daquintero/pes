def sanitize_column_name(column) -> str:
    """
    Converts a list of column names into a sanitized format that only includes
    letters, numbers, and underscores.

    Args:
        columns (List[str]): A list of column names to be sanitized.

    Returns:
        List[str]: A list of sanitized column names.

    Example:
        Input:
            ['(VT("/net05") - VT("/net8")) X', '(VT("/net05") - VT("/net8")) Y']
        Output:
            ['VT_net05_minus_VT_net8_X', 'VT_net05_minus_VT_net8_Y']
    """
    import re

    # Replace special characters with underscores, keeping only letters, numbers, and underscores
    sanitized_column = re.sub(r"[^a-zA-Z0-9 ]", "", column).replace(" ", "_")
    sanitized_column = re.sub(
        r"[^\w\s]", "", sanitized_column
    )  # Remove special characters
    sanitized_column = re.sub(
        r"\s+", "_", sanitized_column
    )  # Replace spaces with underscores
    sanitized_column = sanitized_column.replace("/", "_").replace("-", "_minus_")
    return sanitized_column
