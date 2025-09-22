import awkward as ak
import json
from coffea.processor import ProcessorABC, dict_accumulator
from higgs_to_invisible.utils.objects import select_muons

class CountingProcessor(ProcessorABC):
    def __init__(self, lumi, xsecs, selection_cfg, output_file="yields.json"):
        self._lumi = lumi
        self._xsecs = xsecs
        self._sel = selection_cfg
        self._output_file = output_file
        self._accumulator = dict_accumulator({
            "cutflow": dict_accumulator(),
            "yields": dict_accumulator(),
        })

    @property
    def accumulator(self):
        return self._accumulator

    def process(self, events):
        dataset = events.metadata["dataset"]
        # normalize with lumiWeight and MC weight
        weight = events["weight"] * events["lumiWeight"]
        norm = self._lumi * self._xsecs[dataset] / ak.sum(weight) if ak.sum(weight) != 0 else 0
        evt_weight = weight * norm

        # --- object selection ---
        muons = select_muons(events)
        two_mu = (ak.num(muons) == 2)
        z_window = (events["di_muon_mass"] > self._sel["z_mass_min"]) & (
            events["di_muon_mass"] < self._sel["z_mass_max"]
        )
        met_cut = events["MET"] > self._sel["met_min"]

        # --- signal region selection ---
        sr_sel = two_mu & z_window & met_cut

        # --- store cutflow ---
        out = self.accumulator.identity()
        out["cutflow"][dataset] = {
            "all_events": len(events),
            "2_muons": ak.sum(two_mu),
            "Z_window": ak.sum(two_mu & z_window),
            "SR": ak.sum(sr_sel),
        }

        # --- store SR yield ---
        out["yields"][dataset] = float(ak.sum(evt_weight[sr_sel]))

        return out

    def postprocess(self, accumulator):
        # dump yields to JSON
        out_dict = { "yields": {}, "cutflow": {} }
        for ds in accumulator["yields"]:
            out_dict["yields"][ds] = float(accumulator["yields"][ds])
            out_dict["cutflow"][ds] = dict(accumulator["cutflow"][ds])
        with open(self._output_file, "w") as f:
            json.dump(out_dict, f, indent=2)
        return accumulator
