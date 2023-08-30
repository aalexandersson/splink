import pandas as pd
import pytest

import splink.duckdb.comparison_level_library as clld
import splink.spark.comparison_level_library as clls
from splink.duckdb.linker import DuckDBLinker
from splink.spark.linker import SparkLinker

df = pd.DataFrame(
    [
        {
            "unique_id": 1,
            "first_name": "Andy",
            "last_name": "Williams",
            "postcode": "SE1P 0NY",
        },
        {
            "unique_id": 2,
            "first_name": "Andy's twin",
            "last_name": "Williams",
            "postcode": "SE1P 0NY",
        },
        {
            "unique_id": 3,
            "first_name": "Tom",
            "last_name": "Williams",
            "postcode": "SE1P 0PZ",
        },
        {
            "unique_id": 4,
            "first_name": "Robin",
            "last_name": "Williams",
            "postcode": "SE1P 4UY",
        },
        {
            "unique_id": 5,
            "first_name": "Sam",
            "last_name": "Rosston",
            "postcode": "SE2 7TR",
        },
        {
            "unique_id": 6,
            "first_name": "Ross",
            "last_name": "Samson",
            "postcode": "SW15 8UY",
        },
    ]
)


def postcode_levels(cll):
    return {
        "output_column_name": "postcode",
        "comparison_levels": [
            cll.exact_match_level(
                "postcode", regex_extract="^[A-Z]{1,2}[0-9][A-Z0-9]? [0-9]"
            ),
            cll.levenshtein_level(
                "postcode",
                distance_threshold=1,
                regex_extract="^[A-Z]{1,2}[0-9][A-Z0-9]?",
            ),
            cll.jaro_level(
                "postcode", distance_threshold=1, regex_extract="^[A-Z]{1,2}"
            ),
            cll.else_level(),
        ],
    }


def name_levels(cll):
    return {
        "output_column_name": "name",
        "comparison_levels": [
            cll.jaro_winkler_level(
                "first_name", distance_threshold=1, regex_extract="^[A-Z]{1,4}"
            ),
            cll.columns_reversed_level(
                "first_name", "last_name", regex_extract="[A-Z]{1,3}"
            ),
            cll.else_level(),
        ],
    }


record_pairs_gamma_postcode = {
    3: [(1, 2), (1, 3), (2, 3)],
    2: [(1, 4), (2, 4), (3, 4)],
    1: [(1, 5), (2, 5), (3, 5), (4, 5)],
}

record_pairs_gamma_name = {
    2: [(1, 2), (4, 6)],
    1: [(5, 6)],
}


@pytest.mark.parametrize(
    ("Linker", "df", "level_set", "record_pairs_gamma"),
    [
        pytest.param(
            DuckDBLinker,
            df,
            postcode_levels(clld),
            record_pairs_gamma_postcode,
            id="DuckDB postcode regex levels test",
        ),
        pytest.param(
            DuckDBLinker,
            df,
            name_levels(clld),
            record_pairs_gamma_name,
            id="DuckDB name regex levels test",
        ),
        pytest.param(
            SparkLinker,
            df,
            postcode_levels(clls),
            record_pairs_gamma_postcode,
            id="Spark postcode regex levels test",
        ),
        pytest.param(
            SparkLinker,
            df,
            name_levels(clls),
            record_pairs_gamma_name,
            id="Spark name regex levels test",
        ),
    ],
)
def test_regex(spark, Linker, df, level_set, record_pairs_gamma):
    # Generate settings
    settings = {
        "link_type": "dedupe_only",
        "comparisons": [level_set],
    }

    comparison_name = level_set["output_column_name"]

    if Linker == SparkLinker:
        df = spark.createDataFrame(df)
        df.persist()
    linker = Linker(df, settings)

    linker_output = linker.predict().as_pandas_dataframe()

    for gamma, id_pairs in record_pairs_gamma.items():
        for left, right in id_pairs:
            assert (
                linker_output.loc[
                    (linker_output.unique_id_l == left)
                    & (linker_output.unique_id_r == right)
                ][f"gamma_{comparison_name}"].values[0]
                == gamma
            )


def test_invalid_regex():
    clld.exact_match_level("postcode", regex_extract="^[A-Z]\\d")
    clls.exact_match_level("postcode", regex_extract="^[A-Z]{1}")
    with pytest.raises(SyntaxError):
        clls.exact_match_level("postcode", regex_extract="^[A-Z]\\d")
