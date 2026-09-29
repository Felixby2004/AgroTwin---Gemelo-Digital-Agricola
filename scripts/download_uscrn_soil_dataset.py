from pathlib import Path
import requests


BASE_URL = (
    "https://www.ncei.noaa.gov/"
    "pub/data/uscrn/products/hourly02"
)

OUTPUT_DIR = Path(
    "data/ml/uscrn_raw"
)


def download_file(
    year: int,
    station_filename: str,
) -> Path:

    url = (
        f"{BASE_URL}/"
        f"{year}/"
        f"{station_filename}"
    )

    output_path = (
        OUTPUT_DIR
        / str(year)
        / station_filename
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


    print(
        f"Downloading: {url}"
    )


    response = requests.get(
        url,
        timeout=60,
    )

    response.raise_for_status()


    output_path.write_bytes(
        response.content
    )


    print(
        f"Saved: {output_path}"
    )


    return output_path


def main():

    years = [
        2022,
        2023,
        2024,
        2025,
    ]


    station_suffix = (
        "AZ_Tucson_11_W"
    )


    for year in years:

        filename = (
            f"CRNH0203-"
            f"{year}-"
            f"{station_suffix}.txt"
        )


        try:

            download_file(
                year,
                filename,
            )

        except Exception as exc:

            print(
                f"ERROR {year}: {exc}"
            )


if __name__ == "__main__":

    main()