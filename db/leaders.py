import json

from nba_api.stats.endpoints import leagueleaders


custom_headers = {
    "Host": "stats.nba.com",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
}


def by_year(year, stat):
    """ """
    obj = leagueleaders.LeagueLeaders(
        league_id="00",
        per_mode48="Totals",
        scope="S",
        season=year,
        season_type_all_star="Regular Season",
        stat_category_abbreviation=stat,
        headers=custom_headers,
    )
    return obj.get_dict()["resultSet"]["rowSet"]


YEARS = [
    "2014-15",
    "2015-16",
    "2016-17",
    "2017-18",
    "2018-19",
    "2019-20",
    "2020-21",
]

CATS = [
    "MIN",
    "PTS",
    "REB",
    "STL",
    "BLK",
    "EFF",
    "AST",
    "FTA",
]

if __name__ == "__main__":
    with open("teams.json") as f:
        data = json.load(f)

    history = {}
    for year in YEARS:
        history[year] = {}
        for cat in CATS:
            history[year][cat] = by_year(year, cat)

    totals = {}
    for year, awards in data.items():
        scraped = []
        for award in awards:
            print(year, award)
            totals[award] = []
            for player in awards[award]:
                for cat in CATS:
                    for rank, row in enumerate(history[year][cat]):
                        if row[2] == player:
                            scraped.append([cat, rank + 1, player])
            totals[award].extend(scraped)

    with open("ranks.json", "w+") as f:
        json.dump(totals, f, indent=4)
