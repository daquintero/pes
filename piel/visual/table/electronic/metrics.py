from typing import Optional, Union, Set, List, Dict
from piel.types import RFAmplifierCollection, ComponentMetrics, ScalarMetric
from piel.visual.table.latex import escape_latex

default_metric_header_map = {
    "bandwidth_Hz": r"\textbf{Bandwidth} (GHz)",
    "power_consumption_mW": r"\textbf{Power} (mW)",
    "power_gain_dB": r"\textbf{Power Gain} (dB)",
    "supply_voltage_V": r"\textbf{Supply Voltage} (V)",
    "noise_figure": r"\textbf{Minimum Noise Figure} (dB)",
    "power_added_efficiency": r"\textbf{Power Added Efficiency} (%)",
    "saturated_power_output_dBm": r"\textbf{Saturated Power Output} (dBm)",
    "technology_nm": r"\textbf{CMOS Node}",
    "footprint_mm2": r"\textbf{Footprint} ($mm^2$)",
    "technology_material": r"\textbf{Technology Material}",
    # Add more mappings as needed
}


# Function to format metric values
def format_amplifier_metric(metric: str, metric_obj: Optional[ScalarMetric]) -> str:
    if isinstance(metric_obj, ScalarMetric):
        min_val = getattr(metric_obj, "min", None)
        max_val = getattr(metric_obj, "max", None)
        if min_val is not None and max_val is not None:
            if min_val == max_val:
                value = f"{min_val}"
            else:
                value = f"{min_val} - {max_val}"
        elif min_val is not None:
            value = f"{min_val}"
        else:
            value = "N/A"

        # Specific formatting based on metric type
        try:
            if metric == "bandwidth_Hz":
                min_val = float(getattr(metric_obj, "min", 0))
                max_val = float(getattr(metric_obj, "max", 0))
                if min_val == max_val:
                    value = f"{min_val / 1e9:.2f}"
                else:
                    value = f"{min_val / 1e9:.2f} - {max_val / 1e9:.2f}"
            elif metric == "technology_nm":
                min_val = float(getattr(metric_obj, "min", 0))
                max_val = float(getattr(metric_obj, "max", 0))
                if min_val == max_val:
                    value = f"{int(min_val)}nm"
                else:
                    value = f"{int(min_val)} - {int(max_val)}nm"
            elif metric == "saturated_power_output_dBm":
                min_val = float(getattr(metric_obj, "min", 0))
                max_val = float(getattr(metric_obj, "max", 0))
                if min_val == max_val:
                    value = f"{min_val:.2f}"
                else:
                    value = f"{min_val:.2f} - {max_val:.2f}"
            elif metric == "power_added_efficiency":
                min_val = float(getattr(metric_obj, "min", 0))
                max_val = float(getattr(metric_obj, "max", 0))
                if min_val == max_val:
                    value = f"{min_val:.1f}"
                else:
                    value = f"{min_val:.1f} - {max_val:.1f}"
            elif metric == "footprint_mm2":
                min_val = float(getattr(metric_obj, "min", 0))
                max_val = float(getattr(metric_obj, "max", 0))
                if min_val == max_val:
                    value = f"{min_val:.3f}"
                else:
                    value = f"{min_val:.3f} - {max_val:.3f}"
            elif metric == "power_gain_dB":
                min_val = float(getattr(metric_obj, "min", 0))
                max_val = float(getattr(metric_obj, "max", 0))
                if min_val == max_val:
                    value = f"{min_val:.2f}"
                else:
                    value = f"{min_val:.2f} - {max_val:.2f}"
            elif metric == "power_consumption_mW":
                min_val = float(getattr(metric_obj, "min", 0))
                max_val = float(getattr(metric_obj, "max", 0))
                if min_val == max_val:
                    value = f"{min_val:.2f}"
                else:
                    value = f"{min_val:.2f} - {max_val:.2f}"
            elif metric == "supply_voltage_V":
                min_val = float(getattr(metric_obj, "min", 0))
                max_val = float(getattr(metric_obj, "max", 0))
                if min_val == max_val:
                    value = f"{min_val:.2f}"
                else:
                    value = f"{min_val:.2f} - {max_val:.2f}"
            # Add more specific formatting as needed
        except (ValueError, TypeError):
            value = "N/A"
    else:
        # For non-ScalarMetric or missing metrics
        if metric_obj is not None:
            value = str(metric_obj)
        else:
            value = "N/A"

    # Escape LaTeX special characters
    if isinstance(value, str):
        value = escape_latex(value)

    return value


def compose_amplifier_collection_performance_latex_table(
    amplifier_collection: RFAmplifierCollection,
    desired_metrics: Union[List[str], str] = "*",
    caption: str = "Compiled electronic performance available from the best CMOS LNA and PA literature for successful low-noise and power amplification.",
    label: str = "table:amplifier_designs_review",
    metrics_header_map: Dict[str, str] = default_metric_header_map,
) -> str:
    """
    Composes performance parameters of amplifiers into a LaTeX table,
    handling multiple metrics instances per component.

    Args:
        amplifier_collection (RFAmplifierCollection): The collection of RF amplifiers.
        desired_metrics (List[str] or "*"): List of metric names to include in the table or "*" to include all metrics.
        caption (str): The caption for the LaTeX table.
        label (str): The label for referencing the table in LaTeX.
        metrics_header_map (Dict[str, str]): Mapping from metric names to LaTeX-formatted headers.

    Returns:
        str: A string containing the LaTeX code for the table.
    """
    # Collect all unique metrics if desired_metrics is "*"
    if desired_metrics == "*":
        all_metrics: Set[str] = set()
        for component in amplifier_collection.components:
            metrics_list: List[ComponentMetrics] = getattr(component, "metrics", [])
            for metrics in metrics_list:
                for attr in dir(metrics):
                    if not attr.startswith("_"):
                        attr_value = getattr(metrics, attr)
                        if isinstance(attr_value, ScalarMetric) or isinstance(
                            attr_value, str
                        ):
                            all_metrics.add(attr)
        desired_metrics_list = sorted(all_metrics)
    else:
        desired_metrics_list = desired_metrics

    # Update metric_headers with any new metrics not predefined
    for metric in desired_metrics_list:
        if metric not in metrics_header_map:
            # Generate a LaTeX-friendly header by splitting camelCase or snake_case
            # Example: 'saturated_power_output_dBm' -> 'Saturated Power Output (dBm)'
            parts = metric.split("_")
            if parts[-1].lower() in ["hz", "dbm", "mw", "v", "nm", "mm2"]:
                unit = parts[-1]
                header = (
                    " ".join([part.capitalize() for part in parts[:-1]])
                    + f" ({unit.upper()})"
                )
            else:
                header = " ".join([part.capitalize() for part in parts])
            metrics_header_map[metric] = rf"\textbf{{{header}}}"

    # Initialize LaTeX table string
    # Define column format: one for citation, one for metrics instance, and the rest for metrics
    column_format = "|l|l|" + "X|" * len(desired_metrics_list)

    latex_table = (
        r"""\begin{center}
\begin{table}[h!]
    \centering
    \makebox[\textwidth]{%
        \begin{tabularx}{\textwidth}{"""
        + column_format
        + r"""}
        \hline
        \textbf{Citation} & \textbf{Metrics Instance} & """
        + " & ".join(
            [metrics_header_map.get(metric, metric) for metric in desired_metrics_list]
        )
        + r""" \\
        \hline
"""
    )

    # Iterate over each amplifier component to populate table rows
    for comp_idx, component in enumerate(amplifier_collection.components, start=1):
        metrics_list: List[ComponentMetrics] = getattr(component, "metrics", [])

        if not metrics_list:
            # If no metrics are present, add a single row with Metrics Instance as "N/A"
            citation = "N/A"
            # Attempt to retrieve the BibTeX key from component or its metrics
            reference = None
            if hasattr(component, "metrics") and component.metrics:
                reference = getattr(component.metrics[0], "reference", None)
            if reference and hasattr(reference, "bibtex_id") and reference.bibtex_id:
                citation = f"\\cite{{{escape_latex(reference.bibtex_id)}}}"
            elif hasattr(component, "name") and component.name:
                citation = f"\\cite{{{escape_latex(component.name)}}}"

            row = f"{citation} & N/A & "
            row_entries = ["N/A"] * len(desired_metrics_list)
            row += " & ".join(row_entries) + r" \\" + "\n" + r"\hline" + "\n"
            latex_table += row
            continue

        for metric_idx, metrics in enumerate(metrics_list, start=1):
            # Retrieve the citation
            citation = "N/A"
            reference = getattr(metrics, "reference", None)
            if reference and hasattr(reference, "bibtex_id") and reference.bibtex_id:
                citation = f"\\cite{{{escape_latex(reference.bibtex_id)}}}"
            elif hasattr(component, "name") and component.name:
                citation = f"\\cite{{{escape_latex(component.name)}}}"

            # Start the row with citation and metrics instance
            row = f"{citation} & {metric_idx} & "

            row_entries = []

            for metric in desired_metrics_list:
                metric_obj = getattr(metrics, metric, None)
                entry = format_amplifier_metric(metric, metric_obj)
                row_entries.append(entry)

            row += " & ".join(row_entries) + r" \\" + "\n" + r"\hline" + "\n"
            latex_table += row

    # Close the tabularx and table environments
    latex_table += (
        r"""    \end{tabularx}%
    }
    \caption{"""
        + caption
        + r"""}
    \label{"""
        + label
        + r"""}
\end{table}
\end{center}
"""
    )
    return latex_table
