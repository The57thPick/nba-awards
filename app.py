import pathlib

import streamlit as st
import altair as alt
import pandas as pd

from tinydb import TinyDB, where, Query
from collections import defaultdict

DB = TinyDB("db.json")

YEARS = [
    2014,
    2015,
    2016,
    2017,
    2018,
    2019,
    2020,
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

    st.subheader("🔍 Exploring the data")
    Entry = Query()

    voters = defaultdict(int)
    for row in DB:
        voters[row["Voter"]] += 1

    most = sorted(voters, key=voters.get, reverse=True)  # type: ignore

    data = []
    for i, k in enumerate(most):
        if i > 20:
            break

        q = DB.search(Entry.Voter == k)[0]
        data.append([k, str(voters[k]), q["Affiliation"]])

    df = pd.DataFrame(data, columns=["Name", "Votes", "Affiliation"])

    st.markdown(
        f"""
    Since 2014, there have been a total of `{len(voters)-1}` unique voters. Of
    these individuals, the following have cast the most votes:
    """
    )

    st.dataframe(df)
    st.caption(f"The maximum number of votes is `9` (awards) * `{len(YEARS)}` (years).")
