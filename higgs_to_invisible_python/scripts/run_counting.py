import yaml
from coffea import processor
import uproot

from higgs_to_invisible.processors.counting_processor import CountingProcessor

def main():
    with open("coffea_config/samples.yml") as f:
        samples = yaml.safe_load(f)
    with open("coffea_config/selections.yml") as f:
        selections = yaml.safe_load(f)

    lumi = 5000  # fb^-1
    xsecs = {s: samples[s]["xsec"] for s in samples}

    fileset = {s: {"files": [samples[s]["path"]]} for s in samples}

    proc = CountingProcessor(lumi=lumi, xsecs=xsecs, selection_cfg=selections)

    out = processor.run_uproot_job(
        fileset,
        treename="tree",   # your tree is called "tree"
        processor_instance=proc,
        executor=processor.FuturesExecutor(),
        chunksize=200_000,
    )

    print("Yields:")
    for ds, yld in out["yields"].items():
        print(f"{ds}: {yld:.2f}")

if __name__ == "__main__":
    main()
