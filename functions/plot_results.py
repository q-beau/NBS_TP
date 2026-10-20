# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 14:55:23 2026

@author: qbeau
"""

import os
import re
import glob

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def load_scenarios(results_dir, reporting_years=16):
    """Read all SOC_paramMC_summary_<WS>_<ROT>_<SR>.csv files.

    Returns
    -------
    dict {(WS, ROT, SR): DataFrame} limited to the reporting period.
    """
    pattern = re.compile(r"(?P<WS>[^_]+)_(?P<ROT>[^_]+)_(?P<SR>[^_]+)$")
    scen = {}
    for f in glob.glob(os.path.join(results_dir, "*.csv")):
        key = os.path.splitext(os.path.basename(f))[0].replace("SOC_paramMC_summary_", "")
        m = pattern.search(key)
        if m:
            scen[(m["WS"], m["ROT"], m["SR"])] = pd.read_csv(f).iloc[: reporting_years * 12]
    if not scen:
        raise FileNotFoundError(f"No valid result files found in {results_dir}")
    return scen


def plot_soc_trajectories(scen, show_uncertainty=True):
    """Figure 1: SOC trajectories, one panel per WS x rotation, colour = straw return."""
    WS_list = sorted({k[0] for k in scen}, key=float)
    ROT_list = sorted({k[1] for k in scen})
    SR_list = sorted({k[2] for k in scen}, key=float)
    sr_colors = dict(zip(SR_list, plt.cm.viridis(np.linspace(0.1, 0.9, len(SR_list)))))

    fig, axes = plt.subplots(len(ROT_list), len(WS_list),
                             figsize=(4.2 * len(WS_list), 3.2 * len(ROT_list)),
                             sharex=True, sharey=True, squeeze=False,
                             constrained_layout=True)

    for i, rot in enumerate(ROT_list):
        for j, ws in enumerate(WS_list):
            ax = axes[i, j]
            for sr in SR_list:
                df = scen.get((ws, rot, sr))
                if df is None:
                    continue
                x = df.index / 12
                c = sr_colors[sr]
                ax.plot(x, df["deltaSOC_mean"], color=c, lw=1.8, label=f"Straw return {sr}%")
                if show_uncertainty:
                    ax.fill_between(x, df["deltaSOC_mean"] - df["deltaSOC_sd"],
                                    df["deltaSOC_mean"] + df["deltaSOC_sd"],
                                    color=c, alpha=0.15, lw=0)
            ax.grid(alpha=0.3)
            if i == 0:
                ax.set_title(f"WS {ws}")
            if j == 0:
                ax.set_ylabel(f"{rot}\n SOC stock variation (t/ha)")
            if i == len(ROT_list) - 1:
                ax.set_xlabel("Years since initial date")

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center",
               ncol=len(SR_list), frameon=False)
    fig.suptitle("Simulated SOC stock variation (mean +/- 1 SD)" if show_uncertainty
                 else "Simulated SOC (mean)", fontsize=13)
    return fig


def build_final_delta_table(scen):
    """Final delta SOC (mean, SD) for each scenario."""
    rows = []
    for (ws, rot, sr), df in scen.items():
        if {"deltaSOC_mean", "deltaSOC_sd"} <= set(df.columns):
            rows.append(dict(WS=float(ws), ROT=rot, SR=float(sr),
                             final_SOC=df["deltaSOC_mean"].iloc[-1],
                             final_SOC_sd=df["deltaSOC_sd"].iloc[-1]))
    if not rows:
        raise ValueError("Columns deltaSOC_mean / deltaSOC_sd not found in results")
    return pd.DataFrame(rows).sort_values(["WS", "ROT", "SR"]).reset_index(drop=True)


def plot_final_delta_soc(final_df):
    """Figure 2: final delta SOC (mean +/- SD) by straw return, rotation and WS."""
    SR_vals = sorted(final_df["SR"].unique())
    WS_vals = sorted(final_df["WS"].unique())
    ROT_vals = list(final_df["ROT"].unique())
    rot_colors = dict(zip(ROT_vals, plt.cm.Set2.colors))
    width = 0.6 / len(ROT_vals)

    fig, axes = plt.subplots(1, len(WS_vals), figsize=(4.2 * len(WS_vals), 4),
                             sharey=True, squeeze=False, constrained_layout=True)

    for j, ws in enumerate(WS_vals):
        ax = axes[0, j]
        for k, rot in enumerate(ROT_vals):
            sub = final_df[(final_df.WS == ws) & (final_df.ROT == rot)]
            pos = [SR_vals.index(s) + (k - (len(ROT_vals) - 1) / 2) * width
                   for s in sub.SR]
            ax.errorbar(pos, sub.final_SOC, yerr=sub.final_SOC_sd, fmt="o",
                        capsize=3, color=rot_colors[rot], label=rot)
        ax.axhline(0, color="k", lw=0.8)
        ax.set_xticks(range(len(SR_vals)))
        ax.set_xticklabels([f"{s:g}" for s in SR_vals])
        ax.set_xlabel("Straw return (%)")
        ax.set_title(f"WS {ws:g}")
        ax.grid(alpha=0.3, axis="y")
    axes[0, 0].set_ylabel("Final delta SOC (t/ha)")
    axes[0, -1].legend(title="Rotation", frameon=False, loc="best")
    fig.suptitle("Final delta SOC (mean +/- 1 SD); negative = SOC gain", fontsize=13)
    return fig


def plot_results(results_dir, reporting_years=16, show_uncertainty=True,
                 save=True, dpi=200):
    """Load RothC summaries, produce both figures and report best/worst scenarios.

    Parameters
    ----------
    results_dir : str
        Folder containing the SOC_paramMC_summary_*.csv files.
    reporting_years : int
        Number of years kept from each simulation.
    show_uncertainty : bool
        Draw the +/- 1 SD band on the trajectories.
    save : bool
        Save the figures as PNG in results_dir.
    dpi : int
        Resolution of the saved figures.

    Returns
    -------
    final_df : DataFrame of final delta SOC per scenario
    best, worst : Series of the most / least favorable scenarios
    """
    print("CELL 3: PLOT RESULTS")
    print("=" * 50)

    scen = load_scenarios(results_dir, reporting_years)
    print(f"{len(scen)} scenario(s) loaded")

    plt.close("all")
    fig1 = plot_soc_trajectories(scen, show_uncertainty)
    final_df = build_final_delta_table(scen)
    fig2 = plot_final_delta_soc(final_df)

    if save:
        fig1.savefig(os.path.join(results_dir, "SOC_trajectories.png"), dpi=dpi)
        fig2.savefig(os.path.join(results_dir, "final_deltaSOC.png"), dpi=dpi)
    plt.show()

    best = final_df.loc[final_df["final_SOC"].idxmin()]
    worst = final_df.loc[final_df["final_SOC"].idxmax()]
    print(f"\nMost favorable scenario for SOC storage:\n{best}\n")
    print(f"Least favorable scenario for SOC storage:\n{worst}\n")

    print("=" * 50)
    print("VISUALIZATION COMPLETE")
    if save:
        print(f"Figures saved to: {results_dir}")
    print("=" * 50)

    return final_df, best, worst


def find_scenario(scen, ws, rot, sr):
    """Return the key of scen matching WS/ROT/SR (WS and SR compared as floats)."""
    for (k_ws, k_rot, k_sr) in scen:
        if k_rot == rot and float(k_ws) == float(ws) and float(k_sr) == float(sr):
            return (k_ws, k_rot, k_sr)
    return None


def plot_best_vs_baseline(scen, best, baseline_rot="baselinesubset",
                          baseline_sr=None, show_uncertainty=True,
                          results_dir=None, dpi=200):
    """Compare the SOC time series of the best scenario with its baseline.

    Parameters
    ----------
    scen : dict {(WS, ROT, SR): DataFrame} from load_scenarios().
    best : Series with fields WS, ROT, SR (from plot_results()).
    baseline_rot : str
        Rotation used as reference (same WS as the best scenario).
    baseline_sr : float or None
        Straw return of the baseline. If None, use the same as the best scenario;
        if that combination does not exist, use the lowest available one.
    show_uncertainty : bool
        Draw the +/- 1 SD band.
    results_dir : str or None
        If given, the figure is saved there as PNG.

    Returns
    -------
    fig : matplotlib Figure
    """
    ws, rot, sr = best["WS"], best["ROT"], best["SR"]

    best_key = find_scenario(scen, ws, rot, sr)
    if best_key is None:
        raise KeyError(f"Best scenario not found: WS={ws}, ROT={rot}, SR={sr}")

    target_sr = sr if baseline_sr is None else baseline_sr
    base_key = find_scenario(scen, ws, baseline_rot, target_sr)

    if base_key is None:
        available = sorted((k[2] for k in scen
                            if k[1] == baseline_rot and float(k[0]) == float(ws)),
                           key=float)
        if not available:
            raise KeyError(f"No '{baseline_rot}' scenario found for WS={ws}")
        fallback = available[0]
        print(f"Baseline with SR={target_sr:g} not found; using SR={fallback} "
              f"(available: {', '.join(available)})")
        base_key = find_scenario(scen, ws, baseline_rot, fallback)

    series = [
        (best_key, "#1b7837", f"Best: {best_key[1]} (SR {float(best_key[2]):g}%)"),
        (base_key, "#762a83", f"Baseline: {base_key[1]} (SR {float(base_key[2]):g}%)"),
    ]

    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
    for key, color, label in series:
        df = scen[key]
        x = df.index / 12
        ax.plot(x, df["SOC_mean"], color=color, lw=2.2, label=label)
        if show_uncertainty:
            ax.fill_between(x, df["SOC_mean"] - df["SOC_sd"],
                            df["SOC_mean"] + df["SOC_sd"],
                            color=color, alpha=0.15, lw=0)

    final_best = scen[best_key]["SOC_mean"].iloc[-1]
    final_base = scen[base_key]["SOC_mean"].iloc[-1]
    ax.annotate(f"Final difference: {final_best - final_base:+.2f} t/ha",
                xy=(0.02, 0.96), xycoords="axes fraction", va="top",
                fontsize=10, bbox=dict(boxstyle="round", fc="white", ec="0.7"))

    ax.set_xlabel("Years since initial date")
    ax.set_ylabel("SOC (t/ha)")
    ax.set_title(f"Best scenario vs baseline (WS {float(ws):g})")
    ax.grid(alpha=0.3)
    ax.legend(frameon=False, loc="best")

    if results_dir is not None:
        fig.savefig(os.path.join(results_dir, "best_vs_baseline.png"), dpi=dpi)
    plt.show()
    return fig