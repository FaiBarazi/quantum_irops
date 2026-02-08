from shiny.express import ui, render
from shinywidgets import render_plotly
import polars as pl
import plotly.express as px
import numpy as np
import airportsdata
from utils import get_data_frames

canceled_flights = "./notebooks/data/PRMI-DM_TARGET_FLIGHTS.csv"
available_flights = "./notebooks/data/PRMI-DM-AVAILABLE_FLIGHTS.csv"
all_pnrs = "./notebooks/data/PRMI_DM_ALL_PNRs.csv"

df_affected_flights, df_available_flights, df_pnrs = get_data_frames(
    canceled_flights, available_flights, all_pnrs
)
### Dashboard App ###

with ui.div(
    style="background-color: #363636; padding: 15px 20px; margin-bottom: 20px; border-bottom: 2px solid #444;"
):
    ui.h2(
        "IROPS operations Dashboard", style="color: white; margin: 0; font-weight: 400;"
    )

with ui.layout_columns(col_widths=[6, 6]):
    # Affected PNRs pie chart
    with ui.card():
        ui.card_header("Affected PNRs")

        @render_plotly
        def passenger_pie():
            summary = df_pnrs.group_by("Affected").len().rename({"len": "count"})
            summary = summary.with_columns(
                pl.when(pl.col("Affected") == 1)
                .then(pl.lit("Affected"))
                .otherwise(pl.lit("Non-Affected"))
                .alias("Status")
            )

            fig = px.pie(
                summary,
                values="count",
                names="Status",
                hole=0.4,
                color="Status",
                # Custom colors: Red for affected, Blue for non-affected
                color_discrete_map={"Affected": "#d3462d", "Non-Affected": "#363636"},
            )
            fig.update_traces(textinfo="percent+label")
            return fig

    with ui.card():
        ui.card_header("Affected Flights")

        @render_plotly
        def flight_pie():
            summary_flight = pl.DataFrame(
                {
                    "Status": ["Non-Affected", "Affected"],
                    "Count": [len(df_available_flights), len(df_affected_flights)],
                }
            )

            fig = px.pie(
                summary_flight,
                values="Count",
                names="Status",
                hole=0.4,
                color="Status",
                # Custom colors: Red for affected, Blue for non-affected
                color_discrete_map={"Affected": "#d3462d", "Non-Affected": "#363636"},
            )
            fig.update_traces(textinfo="percent+label")
            return fig
