# Higgs to Invisible Python

Python package for Higgs to Invisible analysis using Coffea, Uproot, and Awkward Array.

## Setting up the python environment
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

source .venv/bin/activate

## Running the analysis
```
python scripts/run_counting.py \
  --config coffea_config/samples.yml \
  --selections coffea_config/selections.yml \
  --systematics coffea_config/systematics.yml \
  --output results/counting_output.coffea
```
```
