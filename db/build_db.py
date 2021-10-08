import csv
import pathlib


from tinydb import TinyDB

if __name__ == "__main__":
    db = TinyDB("db.json")
    for f in pathlib.Path("../data/out").glob("**/*.csv"):
        with f.open("r") as csv_file:
            for row in csv.DictReader(csv_file):
                db.insert(row)
