import os
import csv
import pathlib


from tinydb import TinyDB

if __name__ == "__main__":
    os.remove("db.json")

    db = TinyDB("db.json")
    for f in sorted(pathlib.Path("../data/out").glob("**/*.csv")):
        print(f"Reading {f} ...")
        with f.open("r") as csv_file:
            for row in csv.DictReader(csv_file):
                db.insert(row)
