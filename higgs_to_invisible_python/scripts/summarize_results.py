# scripts/summarize_results.py

import yaml
import json

# --- configuration ---
LUMI = 5000  # fb^-1
GAMMA_SM = 0.00407  # GeV, SM Higgs width for 125 GeV

# example: acceptance*efficiency per signal channel (adjust later)
A_EFF = 0.5  # placeholder, 50%

# background datasets
BACKGROUND_DS = ["BackgroundZZ", "BackgroundWW", "BackgroundTop"]

# --- load yields from processor ---
with open("yields.json") as f:
    yields = json.load(f)

# --- separate signal and background ---
signal_ds = [ds for ds in yields if ds not in BACKGROUND_DS]
background_ds = BACKGROUND_DS

n_signal_obs = sum(yields[ds] for ds in signal_ds)
n_bkg = sum(yields.get(ds, 0) for ds in background_ds)

# --- naive BR estimate ---
n_sig = n_signal_obs - n_bkg
if n_sig < 0:
    n_sig = 0  # avoid negative BR

# Assuming cross-section already included in processor normalization:
# BR = N_sig / (sigma * lumi * A*epsilon)
# For proof-of-principle we can define sigma*lumi = n_signal_obs (already weighted)
BR = n_sig / (n_signal_obs if n_signal_obs > 0 else 1.0)
BR = min(BR, 1.0)

# --- convert to partial width ---
Gamma_inv = BR / (1 - BR) * GAMMA_SM if BR < 1 else GAMMA_SM

# --- print summary ---
print(f"Observed SR counts (signal datasets): {n_signal_obs:.1f}")
print(f"Estimated background: {n_bkg:.1f}")
print(f"Naive signal yield: {n_sig:.1f}")
print(f"Estimated BR(H→inv): {BR:.3f}")
print(f"Estimated partial width Γ_inv: {Gamma_inv*1000:.2f} MeV")  # in MeV

# --- save results ---
results = {
    "n_signal_obs": n_signal_obs,
    "n_background": n_bkg,
    "n_signal_est": n_sig,
    "BR_H_inv": BR,
    "Gamma_inv_GeV": Gamma_inv,
    "Gamma_inv_MeV": Gamma_inv*1000,
}

with open("results_summary.json", "w") as f:
    json.dump(results, f, indent=2)
