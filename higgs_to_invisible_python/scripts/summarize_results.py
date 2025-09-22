import json

# constants
H_TOTAL_WIDTH = 4.07e-3  # GeV
H_SIGMA_ZH = 0.2         # pb @ 250 GeV (example)
LUMI = 5e3               # /fb (example)

def main():
    with open("yields.json") as f:
        results = json.load(f)

    yields = results["yields"]

    # Separate channels
    sig_mm = sum(v for k, v in yields.items() if "SignalZH" in k and k.endswith("_mm"))
    sig_ee = sum(v for k, v in yields.items() if "SignalZH" in k and k.endswith("_ee"))
    bkg_mm = sum(v for k, v in yields.items() if "Background" in k and k.endswith("_mm"))
    bkg_ee = sum(v for k, v in yields.items() if "Background" in k and k.endswith("_ee"))

    # Combined
    sig_total = sig_mm + sig_ee
    bkg_total = bkg_mm + bkg_ee
    obs_total = sig_total + bkg_total

    # Naive BR estimate (proof of principle)
    br_inv = sig_total / (H_SIGMA_ZH * LUMI) if H_SIGMA_ZH * LUMI > 0 else 0.0
    gamma_inv = br_inv * H_TOTAL_WIDTH

    summary = {
        "yields": {
            "signal_mm": sig_mm,
            "signal_ee": sig_ee,
            "background_mm": bkg_mm,
            "background_ee": bkg_ee,
            "signal_total": sig_total,
            "background_total": bkg_total,
            "observed_total": obs_total,
        },
        "results": {
            "BR_Hinv": br_inv,
            "Gamma_Hinv": gamma_inv,
        },
    }

    print("==== H→Invisible Counting Analysis ====")
    print(f"Signal (μμ): {sig_mm:.2f}, Signal (ee): {sig_ee:.2f}")
    print(f"Background (μμ): {bkg_mm:.2f}, Background (ee): {bkg_ee:.2f}")
    print(f"Total Signal: {sig_total:.2f}, Total Background: {bkg_total:.2f}")
    print("---------------------------------------")
    print(f"Naive BR(H→inv): {br_inv:.4e}")
    print(f"Γ(H→inv): {gamma_inv:.4e} GeV")

    with open("results_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    main()
