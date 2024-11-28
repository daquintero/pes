from piel.conversion import convert_array_type
from piel.visual.table.latex import escape_latex


def compose_fock_state_truth_table_latex(
    df,
    headers: list = None,
) -> str:
    latex_table = "\\begin{tabular}{|c|" + "c|" * (len(df.columns)) + "}\n\\hline\n"

    # Column headers
    if headers is None:
        headers = ["$|\\psi_{IN}\\rangle$"] + [
            r"\\texttt{bits}(" + f"$\phi_{i}$)" for i in range(len(df.columns) - 1)
        ]

    latex_table += (
        " & ".join([f"\\textbf{{{escape_latex(header)}}}" for header in headers])
        + " \\\\\n\\hline\n"
    )

    # Rows in Fock state notation
    for _, row in df.iterrows():
        # Convert each bit phase to the desired LaTeX representation
        bit_phases = [
            convert_array_type(row[f"bit_phase_{i}"], output_type="str")
            for i in range(len(headers) - 1)
        ]

        input_fock_state = row["input_fock_state_str"]
        input_state = f"$|{input_fock_state}\\rangle$"

        # Each row formatted for LaTeX
        latex_row = f"{input_state} & " + " & ".join(bit_phases) + " \\\\\n\\hline\n"
        latex_table += latex_row

    # Closing LaTeX syntax
    latex_table += "\\end{tabular}\n"

    return latex_table
