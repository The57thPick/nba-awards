import csv
import pathlib
import json

from collections import defaultdict, OrderedDict

scoring = {
    "MVP": [10, 7, 5, 3, 1],
    "ROY": [5, 3, 1],
    "MIP": [5, 3, 1],
    "DPOY": [5, 3, 1],
    "COY": [5, 3, 1],
    "6th": [5, 3, 1],
}


if __name__ == "__main__":
    results = {}
    for f in pathlib.Path("../data/out").glob("**/*.csv"):
        with f.open("r") as csv_file:
            system = scoring.get(f.stem)
            if not system:
                continue
            entry = defaultdict(int)

            reader = csv.reader(csv_file)
            next(reader)

            for row in reader:
                year = row[-2]
                for idx, player in enumerate(row[2 : len(row) - 2]):
                    if player.lower() == "abstained" or not player:
                        continue
                    entry[player] += system[idx]

            entry = dict(sorted(entry.items(), key=lambda item: item[1], reverse=True))

            results[f"{year}-{f.stem}"] = list(OrderedDict(entry).keys())

    with open("results.json", "w+") as f:
        json.dump(results, f, indent=4)
