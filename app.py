import json
import pathlib

import altair as alt
import pandas as pd
import rbo
import streamlit as st

from tinydb import TinyDB, Query


DL = "https://github.com/The57thPick/nba/releases/download/{year}-media-awards/{year}.zip"
DB = TinyDB("db/db.json")
YEARS = [
    2015,
    2016,
    2017,
    2018,
    2019,
    2020,
    2021,
]
Q = Query()


def truncate(df, col, limit):
    if limit >= len(df):
        limit = len(df) - 1
    return df.sort_values(col)[0:limit]


def award_box(year: str, award: str):
    """ """
    with open("db/ranks.json") as f:
        ranks = json.load(f)
        data = ranks[award]
        return pd.DataFrame(data, columns=["stat", "rank", "player", "year"])


def award_rbo(year: str, award: str):
    """Calculate the Rank-Biased Overlap (RBO) for the given award.

    See https://github.com/changyaochen/rbo.
    """
    data = DB.search((Q.Award == award) & (Q.Year == str(year)))
    non_placements = ["Voter", "Affiliation", "Year", "Award"]

    with open("db/results.json") as f:
        results = json.load(f)
        standard = results.get(f"{year}-{award}")
        if not standard:
            return None

        distance = []
        for i, row in enumerate(data):
            sample = []
            for key in [k for k in row.keys() if k not in non_placements]:
                sample.append(row[key])

            d = rbo.RankingSimilarity(standard, sample).rbo()
            if d == 0:
                # NOTE: This is to ensure that the value is visible on the
                # chart.
                #
                # TODO: A better way?
                d = 0.01
            distance.append([row["Voter"], d, "; ".join(sample)])

    return pd.DataFrame(distance, columns=["Voter", "RBO", "Ballot"])


if __name__ == "__main__":
    st.set_page_config(layout="wide")

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

    st.sidebar.subheader("Controls")
    st.sidebar.caption(
        "Switching the award/year below will dynamically update the content to the right."
    )
    col1, col2 = st.sidebar.columns(2)
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
    limit = st.sidebar.slider(
        "Number of chart results",
        min_value=0,
        max_value=130,
        value=20,
    )

    st.sidebar.subheader("Get the data")
    st.sidebar.markdown(
        f"""
        Download full *{year}* data set [here][1] or browse all available
        data sets [here][2].


        [1]: {DL.format(year=year)}
        [2]: https://github.com/The57thPick/nba/releases
        """
    )

    # Intro
    st.markdown(pathlib.Path("README.md").read_text())

    st.header("❓ Why is this important?")
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

        This exception comes in addition to the well-known
        "[Derrick Rose Rule][3]," which incentivizes making All-NBA teams
        during a player's first four years. In response to the heightened
        stakes of its media-based awards, the NBA also made a [few changes][1]
        to its voter-selection process:

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

    st.header("🔍 Exploring the data")
    st.markdown(
        f"""
        The NBA has 9 distinct media-chosen awards, each with its own number
        of placements and scoring system (more on that later). The table below
        summarizes each voter's ballot for a given award&mdash;Most Valuable
        Player (`MVP`), Coach of the Year (`COY`), Rookie of the Year (`ROY`),
        Defensive Player of the Year (`DPOY`), Most Improved Player (`MIP`),
        6th Man of the Year (`6th`), All-NBA (`All-NBA`), All-Defense
        (`All-Defensive`), or All-Rookie (`All-Rookie`).
        """
    )

    data = DB.search((Q.Award == award) & (Q.Year == str(year)))

    results, headers = [], []
    for i, row in enumerate(data):
        if i == 0:
            headers = row.keys()
        results.append(row.values())

    results_df = pd.DataFrame(results, columns=headers)
    results_df = results_df.drop(["Year", "Award"], axis=1)

    st.dataframe(results_df)
    st.caption("Use the sidebar controls to update the table.")

    st.header("🧮 Analyzing the data")
    st.markdown(
        f"""
        The ultimate goal of this project is to provide a means of assessing
        the *quality* of a given ballot. A common complaint with the
        existing process is that voters are somehow "biased" or are actively
        supporting a certain "agenda." Unfortunately, although it's
        straightforward to describe the perceived problem, it's much harder to
        actually identify it in practice.

        For example, one of the most high-profile cases in recent times was
        [Gary Washburn's decision][2] to select Carmelo Anthony over LeBron
        James as the 2013 MVP, effectively robbing him of the chance to become
        the NBA's first *unanimous* choice (a feat Stephen Curry would later
        accomplish in 2016).

        > "I was heated," James told Chris Haynes, then of Cleveland.com.
        > "But I knew all along [I wasn't getting a unanimous vote]. I just
        > knew it, man."
        >
        > -- [A brief history of LeBron James disagreeing with awards voters][3]

        While you might be tempted to say that identifying *unusual*
        ballots (such as Washburn's) is a good indication of poor choices, it's
        really not that simple&mdash;indeed, what if it's the consensus
        *itself* that's "wrong"?

        This was exactly the case in 2021, [according to Jayson Tatum][1]:

        > “I know I should have made it with the season I had,” Tatum told host
        > Ashley Nevel. “I mean $33 million on the line. Obviously, that would
        > make anyone feel some type of way. And I wasn’t necessarily upset
        > about losing the money. I think I just felt like the way I was
        > playing, everything I did, I thought it should have been a
        > no-brainer. I think I was just more frustrated with that.”

        However, even if it may not be possible to derive objective conclusions
        from an inherently subjective process, we can still perform some
        interesting data analysis.

        [1]: https://www.masslive.com/celtics/2021/06/jayson-tatum-wants-changes-to-all-nba-voting-criteria-after-costly-snub-during-career-year.html
        [2]: http://grantland.com/the-triangle/unanimous-animus-the-lebron-james-mvp-vote-and-debunking-the-myths-of-value/
        [3]: https://www.cbssports.com/nba/news/a-brief-history-of-lebron-james-disagreeing-with-awards-voters-usually-he-has-a-point/
        """
    )

    st.subheader("The Washburn Index")
    st.markdown(
        f"""
        The first type of analysis we'll perform is pretty standard in the
        fields of data science and statistics: the search for outliers in our
        data set.

        But what exactly constitutes an outlier?

        To answer this question, we must first understand the two types of
        ballots: there are *ranked lists* (MVP, COY, DPOY, ...) and *team
        selections* (All-NBA, All-Rookie, and All-defense).

        For ranked-list awards, we define outliers as ballots that are the most
        dissimilar to the final result (the consensus). To help us do this,
        we're going to use the [Rank-Biased Overlap (RBO)][1] metric.

        [1]: https://github.com/changyaochen/rbo
        """
    )

    st.image("./img/rbo.png")
    st.caption(
        "Example RBO values for the 2021 COY award; a lower value implies a more dissimilar result."
    )

    st.markdown(
        """
        The RBO metric is a bounded (`[0, 1]`) similarity measure that includes
        top-weightedness: (dis)agreements at the top of the two lists will
        weigh more heavily than the same (dis)agreement towards to the bottom
        of the lists.

        Below is a visualization of all RBO values for each ranked award (use
        the sidebar to update the chart).
        """
    )

    if "All" not in award:
        rbo_results = award_rbo(year, award)
        rbo_results = truncate(rbo_results, "RBO", limit)

        c = (
            alt.Chart(rbo_results)
            .mark_bar()
            .encode(
                x="RBO",
                y=alt.Y(
                    "Voter",
                    sort=alt.EncodingSortField(field="RBO", order="ascending"),
                    title="",
                ),
                tooltip=["Ballot", "RBO"],
                color=alt.Color(
                    "RBO",
                    scale=alt.Scale(scheme="greenblue", domain=[1, 0], reverse=True),
                ),
            )
        )
        st.altair_chart(c, use_container_width=True)
    else:
        st.warning(
            "The *Washburn Index* only works for ranked awards such as MVP, COY, or DPOY."
        )

    st.subheader("The Tatum Indicator")
    st.markdown(
        f"""
        During the [same interview][1] in which Jayson Tatum expressed his
        displeasure with the 2020-21 All-NBA 3rd Team voting results, he also
        alluded to need for a more objective criteria for making these All-NBA
        teams:

        > “I think what they do need to change is – it’s kind of
        > opinion-based,” he explained. “100 media members have the vote, and
        > what’s the criteria, right? Is there a certain amount of games you
        > need to play. Should you be in playoff contention?
        > ...”

        While the NBA is unlikely to implement such a criteria any time soon,
        the idea leads to an interesting question: Is there an implicit
        criteria that the media follows? We can begin to answer this by
        constructing a profile of what it takes&mdash; *historically*&mdash;to
        make an All-NBA team.

        [1]: https://www.masslive.com/celtics/2021/06/jayson-tatum-wants-changes-to-all-nba-voting-criteria-after-costly-snub-during-career-year.html
        """
    )

    if "All" in award:
        test_df = award_box(year, award)
        c = (
            alt.Chart(test_df)
            .mark_boxplot(extent=0.5)
            .encode(
                x="stat:O",
                y="rank:Q",
                color=alt.Color("stat", legend=None),
                tooltip=["player", "rank", "year"],
            )
        )
        st.altair_chart(c, use_container_width=True)
    else:
        st.warning(
            "The *The Tatum Indicator* only works (currently) for All-NBA teams."
        )

    st.markdown(
        f"""
        The chart above summarizes where each All-NBA team selection ranked in
        a particular stat category. For example, the median rank of players to
        be named to the All-NBA 1st, 2nd, or 3rd team for FTA (free-throws
        attempted) is 12th, while it's only 31st for an All-NBA Defensive
        selection and 101st for an All-Rookie selection.
        """
    )

    st.header("🤔 Conclusion")
    st.markdown(
        """
        The analysis here is really just the beginning; there's a lot more to
        be explored and this page will be updated with new metrics over time.
        If you'd like to performed your own analysis, feel free to download a
        copy of the data from the sidebar.
        """
    )
