from __future__ import annotations

from pathlib import Path
from urllib.request import urlretrieve

import numpy as np
import pandas as pd


# ======================================================
# CONFIGURATION
# ======================================================

BASE_URL = (
    "https://www.ncei.noaa.gov/"
    "pub/data/uscrn/products/hourly02"
)

STATION = "AZ_Yuma_27_ENE"

YEARS = [
    2022,
    2023,
    2024,
    2025,
]

RAW_DIR = Path(
    "data/ml/uscrn_raw"
)

OUTPUT_DIR = Path(
    "data/ml"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "soil_moisture_training.csv"
)


# ======================================================
# USCRN HOURLY02 COLUMNS
# ======================================================

COLUMNS = [
    "WBANNO",
    "UTC_DATE",
    "UTC_TIME",
    "LST_DATE",
    "LST_TIME",
    "CRX_VN",
    "LONGITUDE",
    "LATITUDE",
    "T_CALC",
    "T_HR_AVG",
    "T_MAX",
    "T_MIN",
    "P_CALC",
    "SOLARAD",
    "SOLARAD_FLAG",
    "SOLARAD_MAX",
    "SOLARAD_MAX_FLAG",
    "SOLARAD_MIN",
    "SOLARAD_MIN_FLAG",
    "SUR_TEMP_TYPE",
    "SUR_TEMP",
    "SUR_TEMP_FLAG",
    "SUR_TEMP_MAX",
    "SUR_TEMP_MAX_FLAG",
    "SUR_TEMP_MIN",
    "SUR_TEMP_MIN_FLAG",
    "RH_HR_AVG",
    "RH_HR_AVG_FLAG",
    "SOIL_MOISTURE_5",
    "SOIL_MOISTURE_10",
    "SOIL_MOISTURE_20",
    "SOIL_MOISTURE_50",
    "SOIL_MOISTURE_100",
    "SOIL_TEMP_5",
    "SOIL_TEMP_10",
    "SOIL_TEMP_20",
    "SOIL_TEMP_50",
    "SOIL_TEMP_100",
]


# ======================================================
# DOWNLOAD
# ======================================================

def download_year(
    year: int,
) -> Path:

    filename = (
        f"CRNH0203-"
        f"{year}-"
        f"{STATION}.txt"
    )

    year_dir = (
        RAW_DIR
        / str(year)
    )

    year_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    target = (
        year_dir
        / filename
    )


    if target.exists():

        print(
            f"[SKIP] {target}"
        )

        return target


    url = (
        f"{BASE_URL}/"
        f"{year}/"
        f"{filename}"
    )


    print(
        f"[DOWNLOAD] {url}"
    )


    urlretrieve(
        url,
        target,
    )


    print(
        f"[OK] {target}"
    )


    return target


# ======================================================
# LOAD
# ======================================================

def load_uscrn_file(
    path: Path,
) -> pd.DataFrame:

    return pd.read_csv(
        path,
        sep=r"\s+",
        names=COLUMNS,
        header=None,
        engine="python",
    )


# ======================================================
# TIMESTAMP
# ======================================================

def build_timestamp(
    dataframe: pd.DataFrame,
) -> pd.Series:

    date_text = (
        dataframe[
            "UTC_DATE"
        ]
        .astype(str)
        .str.zfill(8)
    )

    time_text = (
        dataframe[
            "UTC_TIME"
        ]
        .astype(str)
        .str.zfill(4)
    )


    return pd.to_datetime(
        date_text
        + time_text,
        format="%Y%m%d%H%M",
        errors="coerce",
        utc=True,
    )


# ======================================================
# CLEAN NUMERIC VALUES
# ======================================================

def clean_numeric(
    series: pd.Series,
) -> pd.Series:

    values = pd.to_numeric(
        series,
        errors="coerce",
    )


    # USCRN uses negative sentinel
    # values for missing observations.

    values = values.mask(
        values <= -99
    )


    return values


# ======================================================
# CLEAN GEOGRAPHIC COORDINATES
# ======================================================

def clean_latitude(
    series: pd.Series,
) -> pd.Series:

    values = pd.to_numeric(
        series,
        errors="coerce",
    )

    return values.mask(
        (values < -90)
        |
        (values > 90)
    )


def clean_longitude(
    series: pd.Series,
) -> pd.Series:

    values = pd.to_numeric(
        series,
        errors="coerce",
    )

    return values.mask(
        (values < -180)
        |
        (values > 180)
    )

# ======================================================
# EXACT +24 H TARGET
# ======================================================

def add_future_target(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:

    result = (
        dataframe
        .copy()
        .sort_values(
            "timestamp"
        )
        .reset_index(
            drop=True
        )
    )


    future_lookup = (
        result[
            [
                "timestamp",
                "soil_moisture",
            ]
        ]
        .copy()
        .rename(
            columns={
                "soil_moisture":
                    "future_soil_moisture_24h"
            }
        )
    )


    # Convert future timestamp back to
    # the time at which the prediction
    # would have been made.

    future_lookup[
        "timestamp"
    ] = (
        future_lookup[
            "timestamp"
        ]
        - pd.Timedelta(
            hours=24
        )
    )


    result = result.merge(
        future_lookup,
        on="timestamp",
        how="left",
        validate="one_to_one",
    )


    result[
        "soil_moisture_change_24h"
    ] = (
        result[
            "future_soil_moisture_24h"
        ]
        - result[
            "soil_moisture"
        ]
    )


    return result


# ======================================================
# PREPARE
# ======================================================

def prepare_dataset(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:

    result = pd.DataFrame()


    result[
        "timestamp"
    ] = build_timestamp(
        dataframe
    )


    result[
        "station_id"
    ] = STATION

    result[
        "latitude"
    ] = clean_latitude(
        dataframe[
            "LATITUDE"
        ]
    )


    result[
        "longitude"
    ] = clean_longitude(
        dataframe[
            "LONGITUDE"
        ]
    )


    # ==================================================
    # RAW PREDICTORS
    # ==================================================

    result[
        "soil_moisture"
    ] = clean_numeric(
        dataframe[
            "SOIL_MOISTURE_5"
        ]
    )


    result[
        "air_temperature"
    ] = clean_numeric(
        dataframe[
            "T_HR_AVG"
        ]
    )


    result[
        "rainfall"
    ] = clean_numeric(
        dataframe[
            "P_CALC"
        ]
    )


    result[
        "solar_radiation"
    ] = clean_numeric(
        dataframe[
            "SOLARAD"
        ]
    )


    result[
        "relative_humidity"
    ] = clean_numeric(
        dataframe[
            "RH_HR_AVG"
        ]
    )


    result[
        "soil_temperature"
    ] = clean_numeric(
        dataframe[
            "SOIL_TEMP_5"
        ]
    )


    # ==================================================
    # SORT BEFORE TEMPORAL FEATURES
    # ==================================================

    result = (
        result
        .dropna(
            subset=[
                "timestamp"
            ]
        )
        .sort_values(
            "timestamp"
        )
        .drop_duplicates(
            subset=[
                "timestamp"
            ]
        )
        .reset_index(
            drop=True
        )
    )


    # ==================================================
    # TIME FEATURES
    # ==================================================

    result[
        "hour"
    ] = (
        result[
            "timestamp"
        ]
        .dt.hour
    )


    result[
        "day_of_year"
    ] = (
        result[
            "timestamp"
        ]
        .dt.dayofyear
    )


    result[
        "hour_sin"
    ] = np.sin(
        2
        * np.pi
        * result[
            "hour"
        ]
        / 24
    )


    result[
        "hour_cos"
    ] = np.cos(
        2
        * np.pi
        * result[
            "hour"
        ]
        / 24
    )


    result[
        "doy_sin"
    ] = np.sin(
        2
        * np.pi
        * result[
            "day_of_year"
        ]
        / 365.25
    )


    result[
        "doy_cos"
    ] = np.cos(
        2
        * np.pi
        * result[
            "day_of_year"
        ]
        / 365.25
    )


    # ==================================================
    # HISTORICAL FEATURES
    #
    # Only current and past information is used.
    # ==================================================

    result[
        "rainfall_6h"
    ] = (
        result[
            "rainfall"
        ]
        .rolling(
            window=6,
            min_periods=1,
        )
        .sum()
    )


    result[
        "rainfall_24h"
    ] = (
        result[
            "rainfall"
        ]
        .rolling(
            window=24,
            min_periods=1,
        )
        .sum()
    )


    result[
        "temperature_6h_mean"
    ] = (
        result[
            "air_temperature"
        ]
        .rolling(
            window=6,
            min_periods=1,
        )
        .mean()
    )


    result[
        "solar_6h_mean"
    ] = (
        result[
            "solar_radiation"
        ]
        .rolling(
            window=6,
            min_periods=1,
        )
        .mean()
    )


    result[
        "humidity_6h_mean"
    ] = (
        result[
            "relative_humidity"
        ]
        .rolling(
            window=6,
            min_periods=1,
        )
        .mean()
    )


    # ======================================================
    # SOIL MOISTURE HISTORY
    # ======================================================

    result[
        "soil_moisture_lag_1h"
    ] = (
        result[
            "soil_moisture"
        ]
        .shift(1)
    )


    result[
        "soil_moisture_lag_3h"
    ] = (
        result[
            "soil_moisture"
        ]
        .shift(3)
    )


    result[
        "soil_moisture_lag_6h"
    ] = (
        result[
            "soil_moisture"
        ]
        .shift(6)
    )


    result[
        "soil_moisture_lag_12h"
    ] = (
        result[
            "soil_moisture"
        ]
        .shift(12)
    )


    result[
        "soil_moisture_lag_24h"
    ] = (
        result[
            "soil_moisture"
        ]
        .shift(24)
    )


    # ======================================================
    # RECENT SOIL MOISTURE CHANGE
    # ======================================================

    result[
        "soil_moisture_change_1h"
    ] = (
        result[
            "soil_moisture"
        ]
        - result[
            "soil_moisture_lag_1h"
        ]
    )


    result[
        "soil_moisture_change_6h"
    ] = (
        result[
            "soil_moisture"
        ]
        - result[
            "soil_moisture_lag_6h"
        ]
    )


    result[
        "soil_moisture_change_12h"
    ] = (
        result[
            "soil_moisture"
        ]
        - result[
            "soil_moisture_lag_12h"
        ]
    )


    result[
        "soil_moisture_change_previous_24h"
    ] = (
        result[
            "soil_moisture"
        ]
        - result[
            "soil_moisture_lag_24h"
        ]
    )


    # ======================================================
    # LONGER RAIN HISTORY
    # ======================================================

    result[
        "rainfall_48h"
    ] = (
        result[
            "rainfall"
        ]
        .rolling(
            window=48,
            min_periods=1,
        )
        .sum()
    )


    # ==================================================
    # EXACT t + 24 h TARGET
    # ==================================================

    result = add_future_target(
        result
    )


    # ==================================================
    # VALID SOIL MOISTURE
    # ==================================================

    result = result.dropna(
        subset=[
            "soil_moisture",
            "future_soil_moisture_24h",
        ]
    )


    result = result[
        (
            result[
                "soil_moisture"
            ]
            >= 0
        )
        &
        (
            result[
                "soil_moisture"
            ]
            <= 0.8
        )
        &
        (
            result[
                "future_soil_moisture_24h"
            ]
            >= 0
        )
        &
        (
            result[
                "future_soil_moisture_24h"
            ]
            <= 0.8
        )
    ]


    result[
        "year"
    ] = (
        result[
            "timestamp"
        ]
        .dt.year
    )


    return (
        result
        .sort_values(
            "timestamp"
        )
        .reset_index(
            drop=True
        )
    )


# ======================================================
# MAIN
# ======================================================

def main() -> None:

    RAW_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    frames = []


    for year in YEARS:

        path = download_year(
            year
        )


        frame = load_uscrn_file(
            path
        )


        print(
            f"[RAW {year}] "
            f"{len(frame)} rows"
        )


        frames.append(
            frame
        )


    raw = pd.concat(
        frames,
        ignore_index=True,
    )


    dataset = prepare_dataset(
        raw
    )


    dataset.to_csv(
        OUTPUT_FILE,
        index=False,
    )


    print()
    print(
        "=========================================="
    )
    print(
        "USCRN ML DATASET READY"
    )
    print(
        "=========================================="
    )

    print(
        f"Station: {STATION}"
    )

    print(
        f"Rows: {len(dataset)}"
    )

    print(
        f"Start: "
        f"{dataset['timestamp'].min()}"
    )

    print(
        f"End: "
        f"{dataset['timestamp'].max()}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )


    print()
    print(
        "Rows by year:"
    )

    print(
        dataset[
            "year"
        ]
        .value_counts()
        .sort_index()
    )


    print()
    print(
        "Missing predictor values:"
    )

    columns = [
        "soil_moisture",
        "air_temperature",
        "rainfall",
        "solar_radiation",
        "relative_humidity",
        "soil_temperature",
        "rainfall_6h",
        "rainfall_24h",
        "temperature_6h_mean",
        "solar_6h_mean",
        "humidity_6h_mean",
    ]

    print(
        dataset[
            columns
        ]
        .isna()
        .sum()
    )


if __name__ == "__main__":

    main()