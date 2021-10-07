import pathlib

import streamlit as st
import altair as alt
import pandas as pd

from tinydb import TinyDB, where, Query
from collections import defaultdict

DB = TinyDB("db.json")
YEARS = [
    2015,
    2016,
    2017,
    2018,
    2019,
    2020,
    2021,
]


if __name__ == "__main__":
    # Sidebar
    st.sidebar.header("About")
    st.sidebar.markdown(
        """
        The *OpenNBAVoting* project is an effort started by [@jdkato][1] to
        provide machine-readable, standardized access to the NBA's entire
        awards-voting history.

        [1]: https://github.com/jdkato
        """
    )

    st.sidebar.subheader("Get the data")
    st.sidebar.markdown(
        """After every season, we release a standardized CSV file for each
        individual award:
        """
    )
    dl_year = st.sidebar.selectbox("Choose a year", YEARS)

    st.sidebar.markdown(
        f"""
        Download full *{dl_year}* data set [here][1] or browse all available
        data sets [here][2].


        [1]: foo
        [2]: foo
        """
    )

    # Intro
    st.markdown(pathlib.Path("README.md").read_text())

    st.subheader("❓ Why is this important?")
    st.markdown(
        f"""

        In 2016, the NBA players and Board of Governors ratified a new
        [Collective Bargaining Agreement][2]. This agreement included a
        "designated player" exception that allows a team to sign one of its own
        players to a five-year maximum contract extension, according to the
        [following criteria][4]:


        > 1. He makes one of the three all-NBA teams or is named either
             defensive player of the year or most valuable player the previous
             season.
        > 2. He has made one of the three all-NBA teams or has been named
            defensive player of the year in two of the prior three seasons or
            the league’s most valuable player in one of the three prior
            seasons.

        This is exception comes in addition to the well-known
        "[Derrick Rose Rule][3]," which incentivizes making All-NBA teams
        during a player's first four years. In response to the heightened
        stakes of its media-based awards, the NBA also made a [few changes][1]
        to its voter-selection process in 2016:

        > 1. Decreased the number of eligible voters for each award from 130 to 100.
        > 2. Limited the selection pool to "independent" media members (no
           radio/television broadcasters or writers associated with a
           particular team).
        > 3. Required at least one voter per NBA market.

        In total, the NBA's media-based awards have more meaning than ever and
        understanding the process has become all the more important.

        [1]: https://www.yahoo.com/news/nba-alters-voting-process-for-end-of-season-awards-in-quest-for-objectivity-190532014.html
        [2]: https://twitter.com/NBA/status/812446292878102528?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E812446292878102528%7Ctwgr%5E%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fbleacherreport.com%2Farticles%2F2681705-nba-nbpa-agree-on-new-cba-latest-details-comments-reaction
        [3]: http://sports.yahoo.com/news/the-rose-rule--why-it-needs-to-change-150439168.html
        [4]: https://www.washingtonpost.com/news/sports/wp/2016/12/15/a-deeper-look-inside-the-nbas-new-collective-bargaining-agreement/?utm_term=.2497bf5a6a21
        """
    )

    st.subheader("🔍 Exploring the data")
    st.markdown(
        f"""
        The NBA has  9 distinct media-chosen awards, each with its own number
        of placements and scoring system (more on that later).
        """
    )

    awards_df = pd.DataFrame(
        [
            ["Most Valuable Player", "MVP", "1st, 2nd, 3rd, 4th, 5th"],
            ["Coach of the Year", "COY", "1st, 2nd, 3rd"],
            ["Defensive Player of the Year", "DPOY", "1st, 2nd, 3rd"],
            ["Rookie of the Year", "ROY", "1st, 2nd, 3rd"],
            ["Most Improved Player", "MIP", "1st, 2nd, 3rd"],
            ["6th Man of the Year", "6th", "1st, 2nd, 3rd"],
            ["All-NBA Team", "All-NBA", "1st, 2nd, 3rd (5 spots each)"],
            ["All-Rookie Team", "All-Rookie", "1st, 2nd (5 spots each)"],
            ["All-Defensive Team", "All-Defensive", "1st, 2nd (5 spots each)"],
        ],
        columns=["Award", "ID", "Placements"],
    )

    st.dataframe(awards_df)
    st.caption("The `ID` field corresponds to a table in our custom-made database.")

    st.markdown(
        f"""
        Use the drop-down menus below to browse the voting results for specific
        award and year.
        """
    )

    col1, col2 = st.columns(2)

    award = col1.selectbox(
        "Select an award",
        [
            "MVP",
            "COY",
            "DPOY",
            "ROY",
            "MIP",
            "6th",
            "All-NBA",
            "All-Rookie",
            "All-Defensive",
        ],
    )
    year = col2.selectbox("Select a year", YEARS)

    Results = Query()
    data = DB.search((Results.Award == award) & (Results.Year == str(year)))

    results, headers = [], []
    for i, row in enumerate(data):
        if i == 0:
            headers = row.keys()
        results.append(row.values())

    results_df = pd.DataFrame(results, columns=headers)
    st.dataframe(results_df)
