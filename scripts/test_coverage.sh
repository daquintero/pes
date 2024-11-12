# Run from base directory
export COVERAGE_FILE="$(pwd)/.coverage"
echo "$COVERAGE_FILE"
rm $COVERAGE_FILE
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
    # "06_component_codesign_basics.py"  # Uncomment if needed
)

# Change to examples directory
cd docs/examples

# Run each example script with coverage, appending to the same coverage data file
for example in "${examples[@]}"; do
    coverage run --branch --append "$example"
done

# Return to base directory
cd ../../

# Generate the coverage report
coverage report -m
