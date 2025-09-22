import awkward as ak
import numpy as np
import json
from coffea.processor import ProcessorABC, dict_accumulator
from higgs_to_invisible.utils.objects import select_muons, select_electrons

def select_jets(events, pt_min=30, eta_max=4.5):
    mask = (events["jet_pt"] > pt_min) & (abs(events["jet_eta"]) < eta_max)
    return ak.zip({
        "pt": events["jet_pt"][mask],
        "eta": events["jet_eta"][mask],
        "phi": events["jet_phi"][mask],
        "e": events["jet_e"][mask],
    })

def dijet_mass(jets):
    """Compute invariant mass of first two jets per event"""
    E = jets.e[:,0] + jets.e[:,1]
    px = jets.pt[:,0]*np.cos(jets.phi[:,0]) + jets.pt[:,1]*np.cos(jets.phi[:,1])
    py = jets.pt[:,0]*np.sin(jets.phi[:,0]) + jets.pt[:,1]*np.sin(jets.phi[:,1])
    pz = jets.pt[:,0]*np.sinh(jets.eta[:,0]) + jets.pt[:,1]*np.sinh(jets.eta[:,1])
    return np.sqrt(np.maximum(E**2 - px**2 - py**2 - pz**2, 0.0))  # avoid negative sqrt

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
        two_mu = ak.num(muons) == 2
        z_window_mu = (events["di_muon_mass"] > self._sel["z_mass_min_mm"]) & (
                      events["di_muon_mass"] < self._sel["z_mass_max_mm"])
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
        two_e = ak.num(electrons) == 2
        z_window_ee = (events["di_electron_mass"] > self._sel["z_mass_min_ee"]) & (
                      events["di_electron_mass"] < self._sel["z_mass_max_ee"])
        met_cut_ee = events["MET"] > self._sel["met_min_ee"]
        sr_sel_ee = two_e & z_window_ee & met_cut_ee

        out["cutflow"][dataset]["ee"] = {
            "all_events": len(events),
            "2_electrons": ak.sum(two_e),
            "Z_window": ak.sum(two_e & z_window_ee),
            "SR": ak.sum(sr_sel_ee),
        }
        out["yields"][f"{dataset}_ee"] = float(ak.sum(evt_weight[sr_sel_ee]))

        # --- Jet-jet channel ---
        jets = select_jets(events)
        two_jets = ak.num(jets) == 2
        if ak.sum(two_jets) > 0:
            mjj = dijet_mass(jets[two_jets])
            # Broadcast back to full event array
            mjj_full = ak.zeros(len(events))
            mjj_full[two_jets] = mjj
        else:
            mjj_full = ak.zeros(len(events))

        mjj_window = (mjj_full > self._sel["mjj_min"]) & (mjj_full < self._sel["mjj_max"])
        met_cut_jj = events["MET"] > self._sel["met_min_jj"]
        sr_sel_jj = two_jets & mjj_window & met_cut_jj

        out["cutflow"][dataset]["jj"] = {
            "all_events": len(events),
            "2_jets": ak.sum(two_jets),
            "Mjj_window": ak.sum(two_jets & mjj_window),
            "SR": ak.sum(sr_sel_jj),
        }
        out["yields"][f"{dataset}_jj"] = float(ak.sum(evt_weight[sr_sel_jj]))

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
