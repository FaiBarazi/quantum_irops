from shiny.express import ui, render
from shinywidgets import render_plotly
import polars as pl
import plotly.express as px
import numpy as np

# For testing, ideally these need to be env vars and not hard coded.

### DataFrames ###
canceled_flights = "./notebooks/data/PRMI-DM_TARGET_FLIGHTS.csv"
available_flights = "./notebooks/data/PRMI-DM-AVAILABLE_FLIGHTS.csv"
all_pnrs = "./notebooks/data/PRMI_DM_ALL_PNRs.csv"

df_cancelled = pl.read_csv(canceled_flights)
df_all_flights = pl.read_csv(available_flights)
df_pnrs = pl.read_csv(all_pnrs)


df_pnr_cancelled = df_pnrs.join(df_cancelled, on="DEP_KEY", how="semi")

df_pnrs = df_pnrs.with_columns(
    pl.col("DEP_KEY").is_in(df_cancelled["DEP_KEY"]).cast(pl.Int8).alias("Affected")
)


### Dashboard App ###
ui.page_opts(title="IROPS operations Dashboard", fillable=True)

with ui.card():
    ui.card_header("Affected Passengers")
    
    @render_plotly
    def passenger_pie():
        # 1. Group by the 0/1 integer column
        summary = df_pnrs.group_by("Affected").len()

        # 2. Use when/then to create the labels
        # This automatically handles the type conversion from integer to string
        summary = summary.with_columns(
            pl.when(pl.col("Affected") == 1)
            .then(pl.lit("Affected"))
            .otherwise(pl.lit("Non-Affected"))
            .alias("Status")
        )

        # 3. Create the figure
        fig = px.pie(
            summary, 
            values="len", 
            names="Status", 
            hole=0.4,
            color="Status",
            # Custom colors: Red for affected, Blue for non-affected
            color_discrete_map={"Affected": "#ef553b", "Non-Affected": "#636efa"}
        )
        
        fig.update_traces(textinfo='percent+label')
        return fig
