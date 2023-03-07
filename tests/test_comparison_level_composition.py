import pandas as pd
import pytest

import splink.duckdb.duckdb_comparison_level_library as cll
from splink.duckdb.duckdb_linker import DuckDBLinker


def test_misc_checks():
    level = cll.not_(cll.null_level("first_name")).__dict__
    assert level["_level_dict"].get("is_null_level") is None

    # Check that where column_name = None in the level_dict
    # that we don't encounter a breakage
    cll.and_(
        cll.columns_reversed_level("help", "me"),
        cll.columns_reversed_level("help", "me"),
    ).__dict__


@pytest.mark.parametrize(
    ("clause", "c_fun"),
    [
        pytest.param("OR", cll.or_, id="Test or_"),
        pytest.param("AND", cll.and_, id="Test and_"),
    ],
)
def test_composition_internals(clause, c_fun):

    # Test what happens when only one value is fed
    # It should just report the regular outputs of our comparison level func
    level = cll.c_fun(cll.exact_match_level("tom")).__dict__
    assert level["_level_dict"]["sql_condition"] == '("tom_l" = "tom_r")'
    assert level["_level_dict"]["label_for_charts"] == "(Exact match on tom)"

    # Two null levels composed
    level = c_fun(
        cll.null_level("first_name"),
        cll.null_level("surname"),
        label_for_charts="This is a test",
    ).__dict__

    null_sql = (
        f'("first_name_l" IS NULL OR "first_name_r" IS NULL) {clause} '
        '("surname_l" IS NULL OR "surname_r" IS NULL)'
    )
    assert level["_level_dict"]["sql_condition"] == null_sql
    # Default label
    assert level["_level_dict"]["label_for_charts"] == "This is a test"
    assert level["_level_dict"]["is_null_level"] is True

    # Exact match and null level composition
    level = c_fun(
        cll.exact_match_level("first_name"),
        cll.null_level("first_name"),
        m_probability=0.5,
    ).__dict__
    assert (
        level["_level_dict"]["sql_condition"]
        == f'("first_name_l" = "first_name_r") {clause} '
        '("first_name_l" IS NULL OR "first_name_r" IS NULL)'
    )
    # Default label
    assert (
        level["_level_dict"]["label_for_charts"]
        == f"(Exact match on first_name) {clause} (first_name is NULL)"
    )
    # should default to None
    assert level["_level_dict"].get("is_null_level") is None
    assert level["_m_probability"] == 0.5

    # cll.not_(or_(...)) composition
    level = cll.not_(
        c_fun(cll.exact_match_level("first_name"), cll.exact_match_level("surname")),
        m_probability=0.5,
    ).__dict__

    exact_match_sql = (
        f'("first_name_l" = "first_name_r") {clause} ("surname_l" = "surname_r")'
    )
    assert level["_level_dict"]["sql_condition"] == f"NOT ({exact_match_sql})"

    # Check it fails when no inputs are added
    with pytest.raises(ValueError):
        c_fun()


def test_composition_outputs():
    # Check our compositions give expected outputs
    df = pd.DataFrame(
        [
            {
                "unique_id": 1,
                "forename": "Tom",
                "surname": "Tim",
            },
            {
                "unique_id": 2,
                "forename": "Tom",
                "surname": "Tim",
            },
            {
                "unique_id": 3,
                "forename": "Tom",
                "surname": "Timothee",
            },
            {
                "unique_id": 4,
                "forename": "Sam",
                "surname": "Tarly",
            },
            {
                "unique_id": 5,
                "forename": "Sam",
                "surname": "Tim",
            },
        ]
    )

    # For testing the cll version
    dbl_null = cll.or_(cll.null_level("forename"), cll.null_level("surname"))
    both = cll.and_(cll.exact_match_level("forename"), cll.exact_match_level("surname"))
    either = cll.or_(
        cll.exact_match_level("forename"), cll.exact_match_level("surname")
    )

    full_name = {
        "output_column_name": "full_name",
        "comparison_levels": [
            dbl_null,
            both,
            either,
            cll.not_(both),  # acts as an "else" level
            cll.else_level(),
        ],
    }

    settings = {
        "link_type": "dedupe_only",
        "comparisons": [full_name],
    }

    linker = DuckDBLinker(df, settings)

    pred = linker.predict()
    out = pred.as_pandas_dataframe().sort_values(by=["unique_id_l", "unique_id_r"])

    # Check individual IDs are assigned to the correct gamma values
    # Dict key: {gamma_value: tuple of ID pairs}
    size_gamma_lookup = {
        3: [(1, 2)],
        2: [(1, 3), (1, 5), (2, 3), (2, 5), (4, 5)],
        1: [(1, 4), (2, 4), (3, 4), (3, 5)],
    }

    for gamma, id_pairs in size_gamma_lookup.items():
        for l, r in id_pairs:
            assert (
                out.loc[(out.unique_id_l == l) & (out.unique_id_r == r)][
                    "gamma_full_name"
                ].values[0]
                == gamma
            )
