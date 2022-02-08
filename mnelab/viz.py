# Copyright (c) MNELAB developers
#
# License: BSD (3-clause)

import math

import matplotlib.pyplot as plt
from mne.time_frequency import tfr_multitaper
from mne.viz.utils import center_cmap
from mne.viz import plot_compare_evokeds


def _get_rows_cols(n):
    if n <= 3:
        rows, cols = 1, n
    else:
        rows = round(math.sqrt(n))
        cols = math.ceil(math.sqrt(n))
    return rows, cols


def plot_erds(data, freqs, n_cycles, baseline, times=(None, None)):
    tfr = tfr_multitaper(data, freqs, n_cycles, average=False, return_itc=False)
    tfr.apply_baseline(baseline, mode="percent")
    tfr.crop(*times)

    figs = []
    n_rows, n_cols = _get_rows_cols(data.info["nchan"])
    widths = n_cols * [10] + [1]  # each map has width 10, each colorbar width 1

    for event in data.event_id:  # separate figures for each event ID
        fig, axes = plt.subplots(n_rows, n_cols + 1, gridspec_kw={"width_ratios": widths})
        tfr_avg = tfr[event].average()
        vmin, vmax = -1, 2  # default for ERDS maps
        cmap = center_cmap(plt.cm.RdBu, vmin, vmax)
        for ch, ax in enumerate(axes[..., :-1].flat):  # skip last column
            tfr_avg.plot([ch], vmin=vmin, vmax=vmax, cmap=(cmap, False), axes=ax,
                         colorbar=False, show=False)
            ax.set_title(data.ch_names[ch], fontsize=10)
            ax.axvline(0, linewidth=1, color="black", linestyle=":")
            ax.set(xlabel="t (s)", ylabel="f (Hz)")
            ax.label_outer()
        for ax in axes[..., -1].flat:  # colorbars in last column
            fig.colorbar(axes.flat[0].images[-1], cax=ax)

        fig.suptitle(f"ERDS ({event})")
        figs.append(fig)
    return figs


def plot_evoked_comparison(
    epochs,
    picks,
    events,
    average_method,
    combine,
    confidence_intervals,
):
    """
    Plot evoked potentials of different events averaged over channels.

    If multiple channel types are selected, one figure will be returned for
    each channel type.

    Parameters
    ----------
    epochs : mne.epochs.Epochs
        Epochs extracted from a Raw instance.
    picks : list[str]
        Channels to include.
    events : list[str]
        Events to include.
    average_method : {"mean", "median"}
        How to combine the data during averaging.
    combine : {"gfp", "std", mean", "median"}
        How to combine information across channels.
    confidence_intervals : bool
        If `True`, plot confidence intervals as shaded areas.

    Returns
    -------
    list[matplotlib.figure.Figure]
        A list of the figure(s) generated.
    """
    if confidence_intervals:
        evokeds = {e: list(epochs[e].iter_evoked()) for e in events}
    else:
        evokeds = {e: epochs[e].average(picks=picks, method=average_method, by_event_type=True) for e in events}  # noqa: E501
    return plot_compare_evokeds(evokeds, picks=picks, combine=combine)
