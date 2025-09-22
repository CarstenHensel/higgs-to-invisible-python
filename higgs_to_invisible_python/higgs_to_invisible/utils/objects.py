import awkward as ak

def select_muons(events, pt_min=20, eta_max=2.5):
    mask = (events["muon_pt"] > pt_min) & (abs(events["muon_eta"]) < eta_max)
    return ak.zip({
        "pt": events["muon_pt"][mask],
        "eta": events["muon_eta"][mask],
        "phi": events["muon_phi"][mask],
        "e": events["muon_e"][mask],
        "charge": events["muon_charge"][mask],
    })

def select_electrons(events, pt_min=20, eta_max=2.5):
    mask = (events["ele_pt"] > pt_min) & (abs(events["ele_eta"]) < eta_max)
    return ak.zip({
        "pt": events["ele_pt"][mask],
        "eta": events["ele_eta"][mask],
        "phi": events["ele_phi"][mask],
        "e": events["ele_e"][mask],
        "charge": events["ele_charge"][mask],
    })

def select_jets(events, pt_min=30, eta_max=4.5):
    mask = (events["jet_pt"] > pt_min) & (abs(events["jet_eta"]) < eta_max)
    return ak.zip({
        "pt": events["jet_pt"][mask],
        "eta": events["jet_eta"][mask],
        "phi": events["jet_phi"][mask],
        "e": events["jet_e"][mask],
    })
