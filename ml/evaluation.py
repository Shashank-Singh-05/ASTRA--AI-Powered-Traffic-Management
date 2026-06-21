"""
ASTRA ML Pipeline - Evaluation
Consolidated metrics comparison and reporting across all models.
"""

import pandas as pd
import numpy as np
import os
import json

from ml.config import REPORTS_DIR


def compile_evaluation_report(all_results: dict) -> str:
    """Compile a comprehensive evaluation report for all models."""
    print("\n" + "=" * 60)
    print("ASTRA MODEL EVALUATION REPORT")
    print("=" * 60)

    lines = []
    lines.append("=" * 70)
    lines.append("ASTRA - AI-Powered Traffic Decision Intelligence Platform")
    lines.append("MODEL EVALUATION REPORT")
    lines.append("=" * 70)

    # ─── Model 1: Risk Score ───
    if "risk" in all_results:
        lines.append("\n" + "─" * 50)
        lines.append("MODEL 1: Event Impact Risk Score (0-100)")
        lines.append("─" * 50)

        risk = all_results["risk"]
        comparison = []
        for name in ["RF", "XGBoost", "LightGBM"]:
            if name in risk:
                r = risk[name]
                comparison.append({
                    "Model": name,
                    "MAE": round(r["mae"], 2),
                    "RMSE": round(r["rmse"], 2),
                    "R² (test)": round(r["r2_test"], 4),
                    "R² (train)": round(r["r2_train"], 4),
                    "CV R² mean": round(r["cv_r2_mean"], 4),
                    "CV R² std": round(r["cv_r2_std"], 4),
                })
        if comparison:
            comp_df = pd.DataFrame(comparison)
            lines.append(comp_df.to_string(index=False))
            lines.append(f"\nBest Model: {risk.get('best_model', 'N/A')}")
            print(comp_df.to_string(index=False))

    # ─── Model 2: Corridor Stress ───
    if "corridor_stress" in all_results and all_results["corridor_stress"]:
        lines.append("\n" + "─" * 50)
        lines.append("MODEL 2: Corridor Stress Index (0-100)")
        lines.append("─" * 50)

        cs = all_results["corridor_stress"]
        lines.append(f"MAE:  {cs.get('mae', 'N/A')}")
        lines.append(f"RMSE: {cs.get('rmse', 'N/A')}")
        lines.append(f"R²:   {cs.get('r2', 'N/A')}")
        print(f"  Corridor Stress - MAE: {cs.get('mae', 'N/A'):.2f}, "
              f"R²: {cs.get('r2', 'N/A'):.4f}")

    # ─── Model 3: Junction Ranking ───
    if "junction_ranking" in all_results and all_results["junction_ranking"]:
        lines.append("\n" + "─" * 50)
        lines.append("MODEL 3: Junction Risk Ranking")
        lines.append("─" * 50)

        jr = all_results["junction_ranking"]
        lines.append(f"MAE:  {jr.get('mae', 'N/A')}")
        lines.append(f"RMSE: {jr.get('rmse', 'N/A')}")
        lines.append(f"R²:   {jr.get('r2', 'N/A')}")
        if "rankings" in jr:
            n_junctions = len(jr["rankings"])
            lines.append(f"Total junctions ranked: {n_junctions}")
        print(f"  Junction Ranking - MAE: {jr.get('mae', 'N/A'):.2f}, "
              f"R²: {jr.get('r2', 'N/A'):.4f}")

    # ─── Model 4: Duration ───
    if "duration" in all_results:
        dur = all_results["duration"]

        # Regression
        if "regression" in dur:
            lines.append("\n" + "─" * 50)
            lines.append("MODEL 4a: Duration Regression (minutes)")
            lines.append("─" * 50)

            reg = dur["regression"]
            comparison = []
            for name in ["RF", "XGBoost", "LightGBM"]:
                if name in reg:
                    r = reg[name]
                    comparison.append({
                        "Model": name,
                        "MAE (min)": round(r["mae"], 1),
                        "MedAE (min)": round(r["median_ae"], 1),
                        "RMSE (min)": round(r["rmse"], 1),
                        "R²": round(r["r2"], 4),
                    })
            if comparison:
                comp_df = pd.DataFrame(comparison)
                lines.append(comp_df.to_string(index=False))
                lines.append(f"\nBest Model: {reg.get('best_model', 'N/A')}")
                print(f"\n  Duration Regression:")
                print("  " + comp_df.to_string(index=False).replace("\n", "\n  "))

        # Classification
        if "classification" in dur:
            lines.append("\n" + "─" * 50)
            lines.append("MODEL 4b: Duration Classification (Quick/Medium/Long)")
            lines.append("─" * 50)

            clf = dur["classification"]
            comparison = []
            for name in ["RF", "XGBoost", "LightGBM"]:
                if name in clf:
                    r = clf[name]
                    comparison.append({
                        "Model": name,
                        "Accuracy": round(r["accuracy"], 4),
                        "F1 (weighted)": round(r["f1_weighted"], 4),
                    })
            if comparison:
                comp_df = pd.DataFrame(comparison)
                lines.append(comp_df.to_string(index=False))
                lines.append(f"\nBest Model: {clf.get('best_model', 'N/A')}")
                print(f"\n  Duration Classification:")
                print("  " + comp_df.to_string(index=False).replace("\n", "\n  "))

    report_text = "\n".join(lines)

    # Save report
    report_path = os.path.join(REPORTS_DIR, "evaluation_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"\n  ✓ Report saved to {report_path}")

    # Save metrics as JSON
    metrics = {}
    if "risk" in all_results:
        for name in ["RF", "XGBoost", "LightGBM"]:
            if name in all_results["risk"]:
                r = all_results["risk"][name]
                metrics[f"risk_{name}"] = {
                    "mae": r["mae"], "rmse": r["rmse"],
                    "r2_test": r["r2_test"], "cv_r2_mean": r["cv_r2_mean"],
                }
    if "corridor_stress" in all_results and all_results["corridor_stress"]:
        cs = all_results["corridor_stress"]
        metrics["corridor_stress"] = {
            "mae": float(cs.get("mae", 0)),
            "rmse": float(cs.get("rmse", 0)),
            "r2": float(cs.get("r2", 0)),
        }
    if "junction_ranking" in all_results and all_results["junction_ranking"]:
        jr = all_results["junction_ranking"]
        metrics["junction_ranking"] = {
            "mae": float(jr.get("mae", 0)),
            "rmse": float(jr.get("rmse", 0)),
            "r2": float(jr.get("r2", 0)),
        }

    json_path = os.path.join(REPORTS_DIR, "metrics.json")
    with open(json_path, "w") as f:
        json.dump(metrics, f, indent=2, default=str)

    return report_text
