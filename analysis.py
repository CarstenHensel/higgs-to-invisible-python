import uproot
import awkward as ak
import coffea.processor as processor
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema

class HiggsToInvisibleProcessor(processor.ProcessorABC):
    """
    Processor for Higgs to Invisible analysis using Coffea.
    """
    def __init__(self):
        self._accumulator = processor.dict_accumulator({
            "n_events": 0,
            "met": processor.column_accumulator([]),
            "n_jets": processor.column_accumulator([]),
            "n_leptons": processor.column_accumulator([])
        })

    @property
    def accumulator(self):
        return self._accumulator

    def process(self, events):
        output = self.accumulator.copy()
        
        # Count events
        output["n_events"] += len(events)
        
        # Example: missing transverse energy (MET)
        output["met"] += events.MET.pt.to_list()
        
        # Example: jets
        output["n_jets"] += ak.num(events.Jet).to_list()
        
        # Example: leptons
        output["n_leptons"] += ak.num(events.Muon).to_list() + ak.num(events.Electron).to_list()
        
        return output

    def postprocess(self, accumulator):
        return accumulator

from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
from pathlib import Path

def run_analysis(files):
    """
    Run the analysis on one or more ROOT files.
    files can be:
      - a string or Path to a single file
      - a list of strings/Paths with multiple files
    """
    
    # Normalize to list
    if isinstance(files, (str, Path)):
        files = [files]
    elif not isinstance(files, (list, tuple)):
        raise TypeError(f"files must be str, Path, or list of them, got {type(files)}")

    all_events = []
    for f in files:
        events = NanoEventsFactory.from_root(
            str(f),
            treepath="Events",  # adjust to match your tree name
            schemaclass=NanoAODSchema
        ).events()
        all_events.append(events)

    # If just one file, return directly
    if len(all_events) == 1:
        return all_events[0]
    else:
        return all_events  # list of NanoEvents


if __name__ == "__main__":
    files = ["path/to/your/file.root"]  # replace with your files
    results = run_analysis(files)
    print(results)
