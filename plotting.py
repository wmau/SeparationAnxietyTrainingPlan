from datetime import date

import numpy as np
import pandas as pd
import scipy
import seaborn as sns
from matplotlib import pyplot as plt

from gsheet_rw import ethogram_dictionary
import utils

ethogram_conversion = {key: i for i, key in enumerate(ethogram_dictionary.values())}


class EthogramVisualizer:
    def __init__(self, df):
        """
        Contains plotting functions for visualizing ethogram data.

        :parameter
        ---
        df: pandas DataFrame
            Output of EthogramReader.run()
        """
        # Replace the string values of ethogram behaviors with an integer.
        # This is necessary for specifying plot orders of strings.
        self.df = df

        # For plotting, we want the ethogram strings to be converted to
        # numerics to control plot order.
        df_num = df.copy()
        df_num["ethogram"] = df_num["ethogram"].replace(ethogram_conversion)
        self.df_num = df_num
        self.pivoted = self.pivot_ethogram()

    def pivot_ethogram(self):
        pivoted = (
            self.df.pivot_table(
                index="date", columns="ethogram", aggfunc="size", fill_value=0
            )
            .astype(int)
            .reset_index()
        )

        pivoted["total"] = pivoted.sum(axis=1)
        pivoted["date_ordinal"] = pd.to_datetime(pivoted["date"]).apply(
            lambda date: date.toordinal()
        )

        return pivoted

    def plot_ethogram(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(18, 7))
        else:
            fig = ax.figure

        # Plot.
        ax.scatter(self.df_num["observation"], self.df_num["ethogram"], marker="|")

        # Plot session dates.
        dates = utils.get_session_dates(self.df_num)
        for (i, row) in dates.iterrows():
            ax.annotate(
                text=row["date"],
                xy=(row["observation"], ax.get_ylim()[-1]),
                rotation=45,
            )
            ax.axvline(x=row["observation"])

        # Formatting.
        ax.set_xlabel("Observation")
        ax.set_ylabel("Behavior")
        ax.set_yticks(list(ethogram_conversion.values()))
        ax.set_yticklabels(list(ethogram_dictionary.values()))
        [ax.spines[side].set_visible(False) for side in ["top", "right"]]
        fig.tight_layout()

        return fig, ax

    def plot_percent_behavior(self, behavior, ax=None):
        df = self.pivoted.copy()
        df[behavior] = df[behavior] / df["total"]
        pvalue = np.round(
            scipy.stats.spearmanr(df["date_ordinal"], df[behavior]).pvalue, 2
        )

        if ax is None:
            fig, ax = plt.subplots()
        else:
            fig = ax.figure
        sns.regplot(
            data=df,
            x="date_ordinal",
            y=behavior,
            scatter_kws={"s": df["total"] / 5},
            ax=ax,
        )

        new_labels = [date.fromordinal(int(item)) for item in ax.get_xticks()]
        ax.set_xticklabels(new_labels, rotation=45)
        ax.set_title(f"p={pvalue}")
        ax.set_xlabel("Date")
        ax.set_ylabel(f"Proportion spent {behavior}")
        fig.tight_layout()

        return fig, ax


def plot_departures(df, rolling_avg_window):
    df = df.query("type == 'departure'")
    df["date_ordinal"] = pd.to_datetime(df["date"]).apply(lambda date: date.toordinal())
    df["departure_number"] = range(len(df))
    df["rolling_avg"] = df["durations"].rolling(rolling_avg_window).mean()

    fig, ax = plt.subplots()
    ax.scatter(df["departure_number"], df["durations"], s=3, alpha=0.5)
    ax.plot(df["departure_number"], df["rolling_avg"], linewidth=2)

    dates = utils.get_session_dates(df)
    for (i, row) in dates.iterrows():
        ax.annotate(
            text=row["date"],
            xy=(row["departure_number"], ax.get_ylim()[-1]),
            rotation=45,
        )
        ax.axvline(x=row["departure_number"], alpha=0.2)

    ax.set_ylabel("Duration (s)")
    ax.set_xlabel("Departures")
    fig.tight_layout()

    return fig, ax, df

if __name__ == "__main__":
    from main import ReadPipeline

    R = ReadPipeline()
    df = R.read(explode_ethogram=True)
    condensed = R.read(explode_ethogram=False)

    plot_departures(condensed, 15)

    E = EthogramVisualizer(df)
    E.plot_ethogram()
    E.plot_percent_behavior("Away")
    E.plot_percent_behavior("Lying")