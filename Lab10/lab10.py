# Streamlit dashboard for exploring Gapminder data with Plotly and Altair visuals.

from pathlib import Path

import altair as alt
import pandas as pd
import plotly.express as px
import streamlit as st


DATA_PATH = Path(__file__).with_name("gapminder_full.csv")


@st.cache_data
def load_data(csv_path: Path) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def main() -> None:
    st.set_page_config(page_title="Gapminder Dashboard", layout="wide")
    st.title("Lab 10 Dashboard")
    st.write(
        "Scroll to explore continent metrics, GDP vs. life expectancy, and long-run population trends. "
        "Use the controls below to adjust the view."
    )

    df = load_data(DATA_PATH)

    years = sorted(df["year"].unique())
    continents = sorted(df["continent"].unique())

    col_year, col_continent = st.columns([1, 2])
    with col_year:
        selected_year = st.selectbox("Year", options=years, index=years.index(2007) if 2007 in years else len(years) - 1)
    with col_continent:
        selected_continents = st.multiselect(
            "Continents", options=continents, default=continents, help="Applies to all charts."
        )

    if selected_continents:
        filtered_df = df[df["continent"].isin(selected_continents)].copy()
    else:
        filtered_df = df.copy()

    year_df = filtered_df[filtered_df["year"] == selected_year]
    if year_df.empty:
        st.warning("No observations found for the chosen filters.")
        return

    st.header(f"Continent-wise Metrics ({selected_year})")
    bar_metrics = (
        year_df.groupby("continent")
        .agg(
            total_population=("population", "sum"),
            avg_gdp_per_capita=("gdp_cap", "mean"),
            avg_life_expectancy=("life_exp", "mean"),
        )
        .reset_index()
    )
    metric_order = [
        "avg_gdp_per_capita",
        "total_population",
        "avg_life_expectancy",
    ]
    melted_bar = (
        bar_metrics.melt(id_vars="continent", var_name="Metric", value_name="Value")
        .assign(Metric=lambda df_: pd.Categorical(df_["Metric"], categories=metric_order, ordered=True))
        .sort_values(["continent", "Metric"])
    )
    bar_fig = px.bar(
        melted_bar,
        x="continent",
        y="Value",
        color="Metric",
        barmode="group",
        title=f"Population, GDP per Capita, and Life Expectancy ({selected_year})",
        labels={"Value": "Value", "continent": "Continent"},
        category_orders={"Metric": metric_order},
    )
    ordered_continents = bar_metrics["continent"].tolist()
    bar_fig.update_layout(
        xaxis=dict(
            title="Continent",
            type="category",
            categoryorder="array",
            categoryarray=ordered_continents,
            tickmode="array",
            tickvals=ordered_continents,
            ticktext=ordered_continents,
        )
    )
    st.plotly_chart(bar_fig, use_container_width=True)

    st.header(f"GDP per Capita vs. Life Expectancy ({selected_year})")
    scatter_chart = (
        alt.Chart(year_df)
        .mark_circle(size=120, opacity=0.7)
        .encode(
            x=alt.X("gdp_cap:Q", title="GDP per Capita", scale=alt.Scale(type="log")),
            y=alt.Y("life_exp:Q", title="Life Expectancy"),
            color=alt.Color("continent:N", title="Continent"),
            tooltip=["country", "continent", "life_exp", "gdp_cap", "population"],
        )
        .interactive()
    )
    st.altair_chart(scatter_chart, use_container_width=True)

    st.header("Population Trend by Continent")
    line_fig = px.line(
        filtered_df,
        x="year",
        y="population",
        color="continent",
        title="Population Trend Across All Years",
        labels={"year": "Year", "population": "Population", "continent": "Continent"},
    )
    st.plotly_chart(line_fig, use_container_width=True)


if __name__ == "__main__":
    main()
