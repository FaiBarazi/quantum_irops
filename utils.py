import polars as pl
import airportsdata


def get_airport_coord(affected_flights: pl.DataFrame) -> pl.DataFrame:
    iata_dict = airportsdata.load("IATA")
    df_iata = pl.from_dicts(list(iata_dict.values()))
    df_iata = df_iata.select(["iata", "lat", "lon"])
    affected_flights = affected_flights.join(
        df_iata, left_on="ORIG_CD", right_on="iata", how="left"
    ).rename({"lat": "ORIG_LAT", "lon": "ORIG_LONG"})

    affected_flights = affected_flights.join(
        df_iata, left_on="DEST_CD", right_on="iata", how="left"
    ).rename({"lat": "DEST_LAT", "lon": "DEST_LONG"})

    return affected_flights


def get_data_frames(canceled_path, available_path, pnr_path):
    df_affected_flights = pl.read_csv(canceled_path)
    df_affected_flights = get_airport_coord(df_affected_flights)
    df_available_flights = pl.read_csv(available_path)
    df_pnrs = pl.read_csv(pnr_path)

    df_pnrs = df_pnrs.with_columns(
        pl.col("DEP_KEY")
        .is_in(df_affected_flights["DEP_KEY"])
        .cast(pl.Int8)
        .alias("Affected")
    )
    return df_affected_flights, df_available_flights, df_pnrs
