from pathlib import Path
import pandas as pd

PARQUET_PATH = Path("data/final_parquet_pipeline")

df = pd.read_parquet(PARQUET_PATH, engine="pyarrow")

df["din_instante"] = pd.to_datetime(df["din_instante"])


def get_projects():
    projects = (
        df[ 
            ["projeto", "nom_estado", "nom_subsistema"]
        ]
        .drop_duplicates()
        .sort_values("projeto")
    )

    return projects.to_dict(orient="records")


def get_generation_data(
    project_id,
    start_date=None,
    end_date=None,
    frequency="daily"
):
    project_df = df[df["projeto"] == project_id].copy()

    if project_df.empty:
        return None

    if start_date:
        project_df = project_df[project_df["din_instante"] >= start_date]

    if end_date:
        project_df = project_df[project_df["din_instante"] <= end_date]

    if frequency == "daily":
        project_df["period"] = project_df["din_instante"].dt.strftime("%Y-%m-%d")
    else:
        project_df["period"] = project_df["din_instante"].dt.strftime("%Y-%m")

    aggregated = (
        project_df
        .groupby("period")["val_geracao"]
        .sum()
        .reset_index()
    )

    aggregated["projeto"] = project_id

    return aggregated.rename(
        columns={"val_geracao": "total_generation"}
    ).to_dict(orient="records")


def get_restrictions_summary(
    project_id=None,
    start_date=None,
    end_date=None
):
    restriction_df = df.copy()

    if project_id:
        restriction_df = restriction_df[
            restriction_df["projeto"] == project_id
        ]

    if start_date:
        restriction_df = restriction_df[
            restriction_df["din_instante"] >= pd.to_datetime(start_date)
        ]

    if end_date:
        restriction_df = restriction_df[
            restriction_df["din_instante"] <= pd.to_datetime(end_date)
        ]

    restriction_df["cod_razaorestricao"] = (
        restriction_df["cod_razaorestricao"]
        .fillna("WITHOUT_RESTRICTION")
    )

    restriction_df = restriction_df[
        restriction_df["val_geracao"] < restriction_df["val_geracaoreferencia"]
    ].copy()

    restriction_df["restricted_mwh"] = (
        restriction_df["val_geracaoreferencia"]
        - restriction_df["val_geracao"]
    )

    summary = (
        restriction_df
        .groupby("cod_razaorestricao")
        .agg(
            total_hours=("din_instante", "count"),
            total_mwh_restricted=("restricted_mwh", "sum")
        )
        .reset_index()
    )

    return summary.to_dict(orient="records")