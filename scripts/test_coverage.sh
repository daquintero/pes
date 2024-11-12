# Run from base directory
export COVERAGE_FILE="$(pwd)/.coverage"
echo "COVERAGE_FILE: ${COVERAGE_FILE}"
rm -f $COVERAGE_FILE
coverage run --branch -m pytest tests/

# List of example scripts
examples=(
    "03_sax_basics.py"
    "03a_sax_cocotb_cosimulation.py"
    "03b_optical_function_verification.py"
    "04_spice_cosimulation.py"
    "04_spice_cosimulation/04_spice_cosimulation.py"
    "04b_rf_stages_performance.py"
    "05_quantum_integration_basics.py"
    "08_basic_interconnection_modelling/08_basic_interconnection_modelling.py"
    "08a_pcb_interposer_characterisation/08a_pcb_interposer_characterisation.py"
    "09a_model_rf_amplifier/09a_model_rf_amplifier.py"
    "09b_optical_delay/09b_optical_delay.py"
    # "06_component_codesign_basics.py"  # Uncomment if needed
)

# Base directory for examples
examples_dir="docs/examples"

# Run each example script with coverage, appending to the same coverage data file
for example in "${examples[@]}"; do
    echo "Running: ${example}"
    # Full path to the example file
    example_path="$examples_dir/$example"

    # Extract directory and filename
    example_dir="$(dirname "$example_path")"
    example_file="$(basename "$example_path")"

    # Enter the directory
    cd "$example_dir" || exit

    # Run the script with coverage
    coverage run --branch --append "$example_file"
    echo "Appending coverage to: ${COVERAGE_FILE}"
    total=$(coverage report | tail -n1 | awk '{print $NF}' | tr -d '%')
    echo "### Total coverage: ${total}%"

    # Return to base directory
    cd - > /dev/null
done

# Generate the coverage report
coverage report -m
