import csv
import pathlib
import shutil

import camelot
import pandas as pd
import unidecode

from tempfile import NamedTemporaryFile
from nameparser import HumanName


def by_place(n):
    ordinal = lambda n: "%d%s" % (
        n,
        "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10 :: 4],
    )
    headers = ["Voter", "Affiliation"]
    for i in range(1, n + 1):
        headers.append(ordinal(i))
    return headers


def by_position(n):
    headers = ["Voter", "Affiliation"]
    for i in range(1, n + 1):
        headers.extend(
            [
                f"Forward ({i}-1)",
                f"Forward ({i}-2)",
                f"Center ({i}-1)",
                f"Guard ({i}-1)",
                f"Guard ({i}-2)",
            ]
        )
    return headers


AWARD_TO_HEADERS = {
    "MIP": by_place(3),
    "All-Rookie": by_position(2),
    "COY": by_place(3),
    "MVP": by_place(5),
    "6th": by_place(3),
    "All-NBA": by_position(3),
    "ROY": by_place(3),
    "DPOY": by_place(3),
    "All-Defensive": by_position(2),
}


def media_to_csv():
    """Convert the NBA media-voted awards PDF documents into CSV files.

    The PDF documents were downloaded from https://pr.nba.com/ (> 2014) and
    https://official.nba.com/ (<= 2014).
    """
    src = pathlib.Path("src")
    for p in src.glob("**/*.pdf"):
        parsed = str(p).replace("src", "out").replace("pdf", "csv")
        parsed = pathlib.Path(parsed)
        if parsed.exists():
            continue
        parsed.parent.mkdir(exist_ok=True)

        tables = camelot.read_pdf(str(p), pages="all")
        print(f"Extracting {len(tables)} tables from {p.name}...")

        dfs = []
        for table in tables:
            dfs.append(table.df)

        df = pd.concat(dfs, ignore_index=True)
        df.to_csv(str(parsed))


def clean():
    """
    """
    for p in pathlib.Path("out").glob("**/*.csv"):
        headers = AWARD_TO_HEADERS.get(p.stem)
        if not headers:
            print(f"No headers for {p.name}")
            continue
        headers = headers + ["Year", "Award"]

        tempfile = NamedTemporaryFile("w+t", newline="", delete=False)
        with p.open("r") as csvFile, tempfile:
            reader = csv.reader(csvFile, delimiter=",", quotechar='"')
            writer = csv.writer(tempfile, delimiter=",", quotechar='"')

            next(reader, None)

            writer.writerow(headers)
            for row in reader:
                if row[-2] != str(p.parent.name):
                    row.append(str(p.parent.name))
                elif row[-1] != str(p.stem):
                    row.append(str(p.stem))

                if "NBA" in row[0]:
                    row[0] = "Fans"
                    row[1] = "N/A"
                else:
                    name = HumanName(row[0])
                    row[0] = f"{name.first} {name.last}"

                writer.writerow([unidecode.unidecode(s) for s in row])

        shutil.move(tempfile.name, str(p))


if __name__ == "__main__":
    # media_to_csv()
    clean()
