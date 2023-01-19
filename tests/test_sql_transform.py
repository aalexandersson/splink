import sqlglot
from splink.sql_transform import (
    move_l_r_table_prefix_to_column_suffix,
    sqlglot_transform_sql,
)
from splink.athena.athena_transforms import cast_concat_as_varchar
from splink.spark.custom_spark_dialect import Dialect  # noqa 401
from splink.input_column import InputColumn


def move_l_r_test(br, expected):
    res = move_l_r_table_prefix_to_column_suffix(br)
    assert res.lower() == expected.lower()


def test_move_l_r_table_prefix_to_column_suffix():

    br = "l.first_name = r.first_name"
    expected = "first_name_l = first_name_r"
    move_l_r_test(br, expected)

    br = "substr(l.last_name, 1, 2) = substr(r.last_name, 1, 2)"
    expected = "substr(last_name_l, 1, 2) = substr(last_name_r, 1, 2)"
    move_l_r_test(br, expected)

    br = "l.name['first'] = r.name['first'] and levenshtein(l.dob, r.dob) < 2"
    expected = "name_l['first'] = name_r['first'] and levenshtein(dob_l, dob_r) < 2"
    move_l_r_test(br, expected)

    br = "concat_ws(', ', l.name, r.name)"
    expected = "concat_ws(', ', name_l, name_r)"
    move_l_r_test(br, expected)

    br = "my_custom_function(l.name, r.name)"
    expected = "my_custom_function(name_l, name_r)"
    move_l_r_test(br, expected)

    br = "len(list_filter(l.name_list, x -> list_contains(r.name_list, x))) >= 1"
    expected = "len(list_filter(name_list_l, x -> list_contains(name_list_r, x))) >= 1"
    move_l_r_test(br, expected)

    br = "len(list_filter(l.name_list, x -> list_contains(r.name_list, x))) >= 1"
    res = move_l_r_table_prefix_to_column_suffix(br)
    expected = "len(list_filter(name_list_l, x -> list_contains(name_list_r, x))) >= 1"
    assert res.lower() == expected.lower()


def test_cast_concat_as_varchar():

    output = """
        select cast(l.source_dataset as varchar) || '-__-' ||
        cast(l.unique_id as varchar) as concat_id
    """
    output = sqlglot.parse_one(output).sql()

    sql = "select l.source_dataset || '-__-' || l.unique_id as concat_id"
    transformed_sql = sql = sqlglot_transform_sql(sql, cast_concat_as_varchar)
    assert transformed_sql == output

    sql = """
        select cast(l.source_dataset as varchar) || '-__-' ||
        l.unique_id as concat_id
    """
    transformed_sql = sql = sqlglot_transform_sql(sql, cast_concat_as_varchar)
    assert transformed_sql == output

    sql = """
        select cast(l.source_dataset as varchar) || '-__-' ||
        cast(l.unique_id as varchar) as concat_id
    """
    transformed_sql = sql = sqlglot_transform_sql(sql, cast_concat_as_varchar)
    assert transformed_sql == output

    sql = "select source_dataset || '-__-' || unique_id as concat_id"
    transformed_sql = sql = sqlglot_transform_sql(sql, cast_concat_as_varchar)
    assert transformed_sql == output.replace("l.", "")


def test_set_numeric_as_double():
    sql = "select cast('a' as double), cast(0.12345 as double)"
    transformed_sql = sqlglot.transpile(sql, write="customspark")[0]
    assert transformed_sql == "SELECT aD, 0.12345D"

    sql = "select cast('a' as string), cast(0.12345 as double)"
    transformed_sql = sqlglot.transpile(sql, write="customspark")[0]
    assert transformed_sql == "SELECT CAST('a' AS STRING), 0.12345D"


def test_add_pref_and_suffix():
    dull = InputColumn("dull")
    dull_l_r = ['"l"."dull" as "dull_l"', '"r"."dull" as "dull_r"']
    assert dull.l_r_names_as_l_r() == dull_l_r

    assert dull.bf_name() == '"bf_dull"'
    assert dull.tf_name_l() == '"tf_dull_l"'
    tf_dull_l_r = ['"l"."tf_dull" as "tf_dull_l"', '"r"."tf_dull" as "tf_dull_r"']
    assert dull.l_r_tf_names_as_l_r() == tf_dull_l_r

    ll = InputColumn("lat['long']")
    assert ll.name_l() == "\"lat_l\"['long']"

    ll_tf_l_r = [
        '"l"."tf_lat"[\'long\'] as "tf_lat_l"[\'long\']',
        '"r"."tf_lat"[\'long\'] as "tf_lat_r"[\'long\']',
    ]

    assert ll.l_r_tf_names_as_l_r() == ll_tf_l_r

    group = InputColumn("group")
    assert group.name_l() == '"group_l"'
    assert group.bf_name() == '"bf_group"'
    group_l_r_names = ['"l"."group" as "group_l"', '"r"."group" as "group_r"']
    assert group.l_r_names_as_l_r() == group_l_r_names

    group_tf_l_r = ['"l"."tf_group" as "tf_group_l"', '"r"."tf_group" as "tf_group_r"']
    assert group.l_r_tf_names_as_l_r() == group_tf_l_r

    cols = ["unique_id", "SUR name", "group"]
    out_cols = ['"unique_id"', '"SUR name"', '"group"']
    cols_class = [InputColumn(c) for c in cols]
    assert [c.name() for c in cols_class] == out_cols
