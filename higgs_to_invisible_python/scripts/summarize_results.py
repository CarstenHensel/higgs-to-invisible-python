import json

# constants (adjust to your scenario)
H_TOTAL_WIDTH = 4.07e-3  # GeV
H_SIGMA_ZH = 0.2         # pb @ 250 GeV (example)
LUMI = 5e3               # /fb

def main():
    with open("yields.json") as f:
        results = json.load(f)

    yields = results["yields"]

    # Helper to sum channels
    def sum_channel(ch_name):
        return sum(v for k, v in yields.items() if k.endswith(f"_{ch_name}"))

    sig_mm = sum_channel("mm")
    sig_ee = sum_channel("ee")
    sig_jj = sum_channel("jj")
    sig_total = sig_mm + sig_ee + sig_jj

    # Background channels
    bkg_mm = sum(v for k, v in yields.items() if "Background" in k and k.endswith("_mm"))
    bkg_ee = sum(v for k, v in yields.items() if "Background" in k and k.endswith("_ee"))
    bkg_jj = sum(v for k, v in yields.items() if "Background" in k and k.endswith("_jj"))
    bkg_total = bkg_mm + bkg_ee + bkg_jj

    obs_total = sig_total + bkg_total

    # Naive BR and partial width
    br_inv = sig_total / (H_SIGMA_ZH * LUMI) if H_SIGMA_ZH * LUMI > 0 else 0.0
    gamma_inv = br_inv * H_TOTAL_WIDTH

    summary = {
        "yields": {
            "signal_mm": sig_mm,
            "signal_ee": sig_ee,
            "signal_jj": sig_jj,
            "background_mm": bkg_mm,
            "background_ee": bkg_ee,
            "background_jj": bkg_jj,
            "signal_total": sig_total,
            "background_total": bkg_total,
            "observed_total": obs_total,
        },
        "results": {
            "BR_Hinv": br_inv,
            "Gamma_Hinv": gamma_inv,
        },
    }

    # Print summary
    print("==== H→Invisible Counting Analysis ====")
    print(f"Signal (μμ): {sig_mm:.2f}, Signal (ee): {sig_ee:.2f}, Signal (jj): {sig_jj:.2f}")
    print(f"Background (μμ): {bkg_mm:.2f}, Background (ee): {bkg_ee:.2f}, Background (jj): {bkg_jj:.2f}")
    print(f"Total Signal: {sig_total:.2f}, Total Background: {bkg_total:.2f}")
    print("---------------------------------------")
    print(f"Naive BR(H→inv): {br_inv:.4e}")
    print(f"Γ(H→inv): {gamma_inv:.4e} GeV")

    with open("results_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    main()
