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


## Map plot ##
def prepare_flight_paths(df_in):

    df_in = df_in.with_columns(
        (pl.col("C_PAX_CNT") + pl.col("Y_PAX_CNT")).alias("Affected_Passengers")
    )

    valid_flights = df_in.drop_nulls(
        subset=["ORIG_LAT", "ORIG_LONG", "DEST_LAT", "DEST_LONG"]
    )

    origins = valid_flights.select(
        pl.col("DEP_KEY"),
        pl.col("ORIG_LAT").alias("lat"),
        pl.col("ORIG_LONG").alias("lon"),
        pl.lit("Origin").alias("Type"),
        pl.col("Affected_Passengers"),
    )
    dests = valid_flights.select(
        pl.col("DEP_KEY"),
        pl.col("DEST_LAT").alias("lat"),
        pl.col("DEST_LONG").alias("lon"),
        pl.lit("Dest").alias("Type"),
        pl.col("Affected_Passengers"),
    )
    return pl.concat([origins, dests], how="vertical")


df_plot = prepare_flight_paths(df_affected_flights)

with ui.card(full_screen=True, height="500px"):
    ui.card_header("Affected Flight Routes")

    @render_plotly
    def flight_map():
        fig = px.line_mapbox(
            df_plot,
            lat="lat",
            lon="lon",
            line_group="DEP_KEY",
            color="Type",
            mapbox_style="carto-darkmatter",
            zoom=1,
            center={"lat": 20, "lon": 0},
        )

        fig_markers = px.scatter_mapbox(
            df_plot,
            lat="lat",
            lon="lon",
            size="Affected_Passengers",
            size_max=15,
            color="Type",
            hover_name="DEP_KEY",
            mapbox_style="carto-darkmatter",
        )

        fig.add_traces(fig_markers.data)

        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
        )

        fig.update_traces(
            selector=dict(type="scattermapbox", mode="lines"),
            line=dict(width=2, color="#d3462d"),
        )

        return fig
