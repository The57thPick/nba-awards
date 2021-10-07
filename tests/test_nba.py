import csv
import pathlib


def test_media_names():
    for f in pathlib.Path("data/out").glob("**/*.csv"):
        with f.open("r") as csv_file:
            reader = csv.reader(csv_file)
            headings = next(reader)  # Skip the headings
            for idx, row in enumerate(reader):
                # Test 1: Ensure that the first column in each row doesn't
                # contain the substring "voter," which indicates that the row
                # is missing an actual name.
                no_voter = "voter" not in row[0].lower()
                assert no_voter, f"{f} has voter column at {idx+1}"


def test_media_values():
    for f in pathlib.Path("data/out").glob("**/*.csv"):
        with f.open("r") as csv_file:
            reader = csv.reader(csv_file)
            headings = next(reader)  # Skip the headings
            for idx, row in enumerate(reader):
                # Test 2: Ensure that there are no empty columns.
                #
                # There's an empty cell:
                non_empty = all(s != "" and s != "MISSING" for s in row)

                # The voter abstained:
                abstained = any(s.lower() == "abstained" for s in row)

                valid = non_empty or abstained
                assert valid, f"{f} has empty column at {idx+1}"
