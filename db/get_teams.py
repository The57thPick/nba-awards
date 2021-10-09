import re
import json

import bs4
import requests
import unidecode

TEAMS = [
    {
        "url": "https://www.nba.com/news/history-all-defensive-team",
        "name": "All-Defensive",
        "cutoff": 14,
    },
    {
        "url": "https://www.nba.com/news/history-all-nba-teams",
        "name": "All-NBA",
        "cutoff": 20,
    },
    {
        "url": "https://www.nba.com/news/history-all-rookie-teams",
        "name": "All-Rookie",
        "cutoff": 14,
    },
]

YEARS = [
    "2020-21",
    "2019-20",
    "2018-19",
    "2017-18",
    "2016-17",
    "2015-16",
    "2014-15",
]

if __name__ == "__main__":
    name_re = re.compile(r"(?:[A-Z]{1}:|•)([^,]+),")

    results = {}
    for year in YEARS:
        results[year] = {}

    for team in TEAMS:
        page = requests.get(team["url"])
        soup = bs4.BeautifulSoup(page.content, "html.parser")
        for h in soup.find_all("h3"):
            year = h.text
            if year not in YEARS:
                continue
            hr = h.findNext("hr")

            players = []
            for p in hr.find_all_previous("p")[0 : team["cutoff"]]:
                m = name_re.match(p.text)
                if m:
                    name = unidecode.unidecode(m.group(1).strip())
                    players.append(name)

            results[year][team["name"]] = players

    with open("teams.json", "w+") as f:
        json.dump(results, f, indent=4)
