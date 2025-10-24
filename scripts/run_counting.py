#!/usr/bin/env python
import yaml
from coffea.processor import run_uproot_job
from coffea.nanoevents import NanoAODSchema
from counting_processor import CountingProcessor
import os

# -----------------------------
# User configuration
# -----------------------------
LUMI = 5e3  # /fb
XSECS = {
    "SignalZH": 0.2,       # pb
    "BackgroundZZ": 0.5,
    "BackgroundWW": 0.6,
}

FILES = {
    "SignalZH": ["ntuples/signal_*.root"],
    "BackgroundZZ": ["ntuples/bkg_zz_*.root"],
    "BackgroundWW": ["ntuples/bkg_ww_*.root"],
}

PROCESSOR_EXECUTOR = "futures"
EXECUTOR_ARGS = {"workers": 4, "schema": NanoAODSchema}

# -----------------------------
# Load selections from YAML
# -----------------------------
with open("coffea_config/selections.yml") as f:
    selection_cfg = yaml.safe_load(f)

# -----------------------------
# Instantiate the processor
# -----------------------------
processor = CountingProcessor(
    lumi=LUMI,
    xsecs=XSECS,
    selection_cfg=selection_cfg,
    output_file="yields.json"
)

# -----------------------------
# Run the coffea job
# -----------------------------
output = run_uproot_job(
    fileset=FILES,
    treename="tree",
    processor_instance=processor,
    executor=PROCESSOR_EXECUTOR,
    executor_args=EXECUTOR_ARGS,
)

print("Counting finished. Yields written to yields.json")
