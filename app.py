import pathlib

import streamlit as st

DATA = "https://github.com/The57thPick/nba/tree/main/data/media/out/{year}"


if __name__ == "__main__":
    st.markdown(
        """
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-F3w7mX95PdgyTmZZMECAngseQB83DfGTowi0iMjiWaeVhAn4FJkqJByhZMI3AhiU" crossorigin="anonymous">
        """,
        unsafe_allow_html=True,
    )

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
    dl_year = st.sidebar.selectbox(
        "Choose a year",
        [
            2014,
            2015,
            2016,
            2017,
            2018,
            2019,
            2020,
        ],
    )

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
