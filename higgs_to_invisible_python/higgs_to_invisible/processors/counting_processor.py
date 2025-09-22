import awkward as ak
from coffea.processor import ProcessorABC, dict_accumulator
from higgs_to_invisible.utils.objects import select_muons, select_electrons, select_jets

class CountingProcessor(ProcessorABC):
    def __init__(self, lumi, xsecs, selection_cfg):
        self._lumi = lumi
        self._xsecs = xsecs
        self._sel = selection_cfg
        self._accumulator = dict_accumulator({
            "cutflow": dict_accumulator(),
            "yields": dict_accumulator(),
        })

    @property
    def accumulator(self):
        return self._accumulator

    def process(self, events):
        dataset = events.metadata["dataset"]
        weight = events["weight"] * events["lumiWeight"]
        norm = self._lumi * self._xsecs[dataset] / ak.sum(weight) if ak.sum(weight) != 0 else 0
        evt_weight = weight * norm

        # channel: Z→μμ
        muons = select_muons(events)
        two_mu = (ak.num(muons) == 2)
        z_window = (events["di_muon_mass"] > self._sel["z_mass_min"]) & (
            events["di_muon_mass"] < self._sel["z_mass_max"]
        )
        met_cut = events["MET"] > self._sel["met_min"]

        sr_sel = two_mu & z_window & met_cut

        # yields
        sr_yield = ak.sum(evt_weight[sr_sel])

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
