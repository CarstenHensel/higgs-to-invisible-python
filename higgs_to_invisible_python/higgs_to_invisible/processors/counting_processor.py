import awkward as ak
import json
from coffea.processor import ProcessorABC, dict_accumulator
from higgs_to_invisible.utils.objects import select_muons, select_electrons

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

        out = self.accumulator.identity()
        out["cutflow"][dataset] = {}
        
        # --- Muon channel ---
        muons = select_muons(events)
        two_mu = (ak.num(muons) == 2)
        z_window_mu = (events["di_muon_mass"] > self._sel["z_mass_min_mm"]) & (
            events["di_muon_mass"] < self._sel["z_mass_max_mm"]
        )
        met_cut_mu = events["MET"] > self._sel["met_min_mm"]
        sr_sel_mu = two_mu & z_window_mu & met_cut_mu

        out["cutflow"][dataset]["mm"] = {
            "all_events": len(events),
            "2_muons": ak.sum(two_mu),
            "Z_window": ak.sum(two_mu & z_window_mu),
            "SR": ak.sum(sr_sel_mu),
        }
        out["yields"][f"{dataset}_mm"] = float(ak.sum(evt_weight[sr_sel_mu]))

        # --- Electron channel ---
        electrons = select_electrons(events)
        two_e = (ak.num(electrons) == 2)
        z_window_ee = (events["di_electron_mass"] > self._sel["z_mass_min_ee"]) & (
            events["di_electron_mass"] < self._sel["z_mass_max_ee"]
        )
        met_cut_ee = events["MET"] > self._sel["met_min_ee"]
        sr_sel_ee = two_e & z_window_ee & met_cut_ee

        out["cutflow"][dataset]["ee"] = {
            "all_events": len(events),
            "2_electrons": ak.sum(two_e),
            "Z_window": ak.sum(two_e & z_window_ee),
            "SR": ak.sum(sr_sel_ee),
        }
        out["yields"][f"{dataset}_ee"] = float(ak.sum(evt_weight[sr_sel_ee]))

        return out

    def postprocess(self, accumulator):
        # dump yields to JSON
        out_dict = { "yields": {}, "cutflow": {} }
        for ds in accumulator["yields"]:
            out_dict["yields"][ds] = float(accumulator["yields"][ds])
        
        for ds in accumulator["cutflow"]:
            out_dict["cutflow"][ds] = dict(accumulator["cutflow"][ds])
        
        with open(self._output_file, "w") as f:
            json.dump(out_dict, f, indent=2)
        return accumulator
