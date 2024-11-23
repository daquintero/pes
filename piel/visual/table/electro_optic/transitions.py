from piel.conversion import convert_array_type
from piel.visual.table.latex import escape_latex
from piel.visual.table.symbol import convert_tuple_to_pi_fractions


# Combined function to convert DataFrame to Fock state formatted LaTeX table
def compose_optical_state_transition_dataframe_latex_table(
    df,
    headers: list = None,
) -> str:
    latex_table = "\\begin{tabular}{|c|c|c|c|}\n\\hline\n"

    # Column headers
    if headers is None:
        headers = [
            "$(\\phi_{0},...,\phi_{N})$",
            "$|\\psi_{IN}\\rangle$",
            "$|\\psi_{OUT}\\rangle$",
            "Target",
        ]

    latex_table += (
        " & ".join([f"\\textbf{{{escape_latex(header)}}}" for header in headers])
        + " \\\\\n\\hline\n"
    )

    # Rows in Fock state notation
    for _, row in df.iterrows():
        symbolic_phase = convert_tuple_to_pi_fractions(row["phase"])
        # print(symbolic_phase)
        phase = symbolic_phase  # Convert tuple to string before escaping
        input_fock_state = convert_array_type(
            row["input_fock_state"], output_type="str"
        )
        output_fock_state = convert_array_type(
            row["output_fock_state"], output_type="str"
        )

        input_state = (
            f"$|{input_fock_state}\\rangle$"  # Removes parentheses and adds |...⟩
        )
        output_state = f"$|{output_fock_state}\\rangle$"
        target_mode_output = row["target_mode_output"]

        # Each row formatted for LaTeX
        latex_row = f"{phase} & {input_state} & {output_state} & {target_mode_output} \\\\\n\\hline\n"
        latex_table += latex_row

    # Closing LaTeX syntax
    latex_table += "\\end{tabular}\n"

    return latex_table
