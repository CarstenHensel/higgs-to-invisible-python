# higgs_to_invisible/processors/counting_processor.py

import awkward as ak
import numpy as np
from coffea.processor import ProcessorABC, dict_accumulator

from higgs_to_invisible.utils.objects import select_muons, select_jets, compute_met

class CountingProcessor(ProcessorABC):
    def __init__(self, lumi, xsecs):
        self._lumi = lumi
        self._xsecs = xsecs
        self._accumulator = dict_accumulator({
            "cutflow": dict_accumulator(),
            "yields": dict_accumulator(),
        })

    @property
    def accumulator(self):
        return self._accumulator

    def process(self, events):
        dataset = events.metadata["dataset"]
        weight = self._lumi * self._xsecs[dataset] / len(events)

        # --- object selections ---
        muons = select_muons(events.Muon)
        jets  = select_jets(events.Jet)
        met   = compute_met(events)

        # --- example SR: Z->mumu + MET ---
        two_mu = (ak.num(muons) == 2)
        mll    = (ak.firsts((muons[:,0] + muons[:,1]).mass))
        z_window = (mll > 80) & (mll < 100)
        met_cut  = (met.pt > 100)

        sr_sel = two_mu & z_window & met_cut
        sr_yield = ak.sum(sr_sel) * weight

        # --- store ---
        out = self.accumulator.identity()
        out["yields"][dataset] = sr_yield
        out["cutflow"][dataset] = {
            "all": len(events),
            "2mu": ak.sum(two_mu),
            "zwin": ak.sum(two_mu & z_window),
            "sr": ak.sum(sr_sel),
        }
        return out

    def postprocess(self, accumulator):
        return accumulator
