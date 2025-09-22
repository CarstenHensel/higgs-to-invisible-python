# scripts/run_counting.py

import yaml
from coffea import processor, nanoevents
from coffea.nanoevents import NanoAODSchema  # or your schema

from higgs_to_invisible.processors.counting_processor import CountingProcessor

def main():
    # load configs
    with open("coffea_config/samples.yml") as f:
        samples = yaml.safe_load(f)
    with open("coffea_config/xsecs.yml") as f:
        xsecs = yaml.safe_load(f)

    lumi = 5_000  # fb^-1, adjust

    fileset = {s: {"files": [samples[s]["path"]]} for s in samples}

    proc = CountingProcessor(lumi=lumi, xsecs=xsecs)
    out = processor.run_uproot_job(
        fileset,
        treename="events",   # adjust to your ntuple tree name
        processor_instance=proc,
        executor=processor.FuturesExecutor(),
        chunksize=500_000,
    )

    print("Yields:")
    for ds, yld in out["yields"].items():
        print(f"{ds}: {yld:.2f}")

if __name__ == "__main__":
    main()
