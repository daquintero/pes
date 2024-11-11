# Run from base directory
coverage run -m pytest tests/

# List of example scripts
examples=(
    "03_sax_basics.py" \
    "03a_sax_cocotb_cosimulation.py" \
    "03b_optical_function_verification.py" \
    "04_spice_cosimulation.py" \
#    "06_component_codesign_basics.py" \
)

# Run each example script with coverage, appending to the same coverage data
for example in "${examples[@]}"; do
    coverage run --append "docs/examples/$example"
done
