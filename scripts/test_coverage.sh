# Run from base directory
coverage run -m pytest tests/

# List of example scripts
examples=("03_sax_basics.py" )

# Run each example script with coverage, appending to the same coverage data
for example in "${examples[@]}"; do
    coverage run --append "docs/examples/$example"
done
