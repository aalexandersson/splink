from __future__ import annotations

import re
import string
from copy import copy
from functools import partial
from typing import Protocol, Union

import sqlglot

from splink.internals.dialects import SplinkDialect
from splink.input_column import SqlglotColumnTreeBuilder
from splink.sql_transform import (
    add_suffix_to_all_column_identifiers,
    add_table_to_all_column_identifiers,
)


class ColumnExpressionOperation(Protocol):
    def __call__(self, name: str, dialect: SplinkDialect) -> str: ...


class ColumnExpression:
    """
    Enables transforms to be applied to a column before it's passed into a
    comparison level.

    Dialect agnostic.  Execution is delayed until the dialect is known.

    For example:
        from splink.column_expression import ColumnExpression
        col = (
            ColumnExpression("first_name")
            .lower()
            .regex_extract("^[A-Z]{1,4}")
        )

        ExactMatchLevel(col)

    Note that this will typically be created without a dialect, and the dialect
    will later be populated when the ColumnExpression is passed via a comparison
    level creator into a linker.
    """

    def __init__(self, sql_expression: str, sql_dialect: SplinkDialect = None):
        self.raw_sql_expression = sql_expression
        self.operations: list[ColumnExpressionOperation] = []
        if sql_dialect is not None:
            self.sql_dialect: SplinkDialect = sql_dialect

    def _clone(self) -> "ColumnExpression":
        clone = copy(self)
        clone.operations = [op for op in self.operations]
        return clone

    @staticmethod
    def instantiate_if_str(
        str_or_column_expression: Union[str, "ColumnExpression"],
    ) -> "ColumnExpression":
        if isinstance(str_or_column_expression, ColumnExpression):
            return str_or_column_expression
        elif isinstance(str_or_column_expression, str):
            return ColumnExpression(str_or_column_expression)

    def parse_input_string(self, dialect: SplinkDialect) -> str:
        """
        The input into an ColumnExpression can be
            - a column name or column reference e.g. first_name, first name
            - a sql expression e.g. UPPER(first_name), first_name || surname

        In the former case, we do not expect the user to have escaped the column name
        with identifier quotes (see also InputColumn).

        In the later case, we expect the expression to be valid sql in the dialect
        that the user will specify in their linker.
        """

        if not self.raw_sql_is_pure_column_or_column_reference:
            return self.raw_sql_expression

        return SqlglotColumnTreeBuilder.from_raw_column_name_or_column_reference(
            self.raw_sql_expression, dialect.sqlglot_name
        ).sql

    @property
    def raw_sql_is_pure_column_or_column_reference(self) -> bool:
        # It's difficult (possibly impossible) to find a completely general
        # algorithm that can distinguish between the two cases (col name, or sql
        # expression), since lower(first_name) could technically be a column name
        # Here I use a heuristic:
        # If there's a () or || then assume it's a sql expression
        if re.search(r"\([^)]*\)", self.raw_sql_expression):
            return False

        if "||" in self.raw_sql_expression:
            return False
        return True

    @property
    def is_pure_column_or_column_reference(self) -> bool:
        if len(self.operations) > 0:
            return False

        return self.raw_sql_is_pure_column_or_column_reference

    def apply_operations(self, name: str, dialect: SplinkDialect) -> str:
        for op in self.operations:
            name = op(name=name, dialect=dialect)
        return name

    def _lower_dialected(self, name: str, dialect: SplinkDialect) -> str:
        lower_sql = sqlglot.parse_one("lower(___col___)").sql(
            dialect=dialect.sqlglot_name
        )

        return lower_sql.replace("___col___", name)

    def lower(self) -> "ColumnExpression":
        """
        Applies a lowercase transform to the input expression.
        """
        clone = self._clone()
        clone.operations.append(clone._lower_dialected)
        return clone

    def _substr_dialected(
        self, name: str, start: int, end: int, dialect: SplinkDialect
    ) -> str:
        substr_sql = sqlglot.parse_one(f"substring(___col___, {start}, {end})").sql(
            dialect=dialect.sqlglot_name
        )

        return substr_sql.replace("___col___", name)

    def substr(self, start: int, length: int) -> "ColumnExpression":
        """
        Applies a substring transform to the input expression of a given length
        starting from a specified index.
        Args:
            start (int): The starting index of the substring.
            length (int): The length of the substring.
        """
        clone = self._clone()
        op = partial(clone._substr_dialected, start=start, end=length)
        clone.operations.append(op)

        return clone

    def _cast_to_string_dialected(self, name: str, dialect: SplinkDialect) -> str:
        cast_sql = sqlglot.parse_one("cast(___col___ as string)").sql(
            dialect=dialect.sqlglot_name
        )
        return cast_sql.replace("___col___", name)

    def cast_to_string(self) -> "ColumnExpression":
        """
        Applies a cast to string transform to the input expression.
        """
        clone = self._clone()
        op = partial(clone._cast_to_string_dialected)
        clone.operations.append(op)

        return clone

    def _regex_extract_dialected(
        self,
        name: str,
        pattern: str,
        capture_group: int,
        dialect: SplinkDialect,
    ) -> str:
        # must use dialect specific functions because sqlglot doesn't yet support the
        # position (capture group) arg
        return dialect.regex_extract(
            name,
            pattern=pattern,
            capture_group=capture_group,
        )

    def regex_extract(self, pattern: str, capture_group: int = 0) -> "ColumnExpression":
        """Applies a regex extract transform to the input expression.

        Args:
            pattern (str): The regex pattern to match.
            capture_group (int): The capture group to extract from the matched pattern.
                Defaults to 0, meaning the full pattern is extracted

        """
        clone = self._clone()
        op = partial(
            clone._regex_extract_dialected,
            pattern=pattern,
            capture_group=capture_group,
        )
        clone.operations.append(op)

        return clone

    def _try_parse_date_dialected(
        self,
        name: str,
        dialect: SplinkDialect,
        date_format: str = None,
    ) -> str:
        return dialect.try_parse_date(name, date_format=date_format)

    def try_parse_date(self, date_format: str = None) -> "ColumnExpression":
        clone = self._clone()
        op = partial(
            clone._try_parse_date_dialected,
            date_format=date_format,
        )
        clone.operations.append(op)

        return clone

    def _try_parse_timestamp_dialected(
        self,
        name: str,
        dialect: SplinkDialect,
        timestamp_format: str = None,
    ) -> str:
        return dialect.try_parse_timestamp(name, timestamp_format=timestamp_format)

    def try_parse_timestamp(self, timestamp_format: str = None) -> "ColumnExpression":
        clone = self._clone()
        op = partial(
            clone._try_parse_timestamp_dialected,
            timestamp_format=timestamp_format,
        )
        clone.operations.append(op)

        return clone

    @property
    def name(self) -> str:
        sql_expression = self.parse_input_string(self.sql_dialect)
        return self.apply_operations(sql_expression, self.sql_dialect)

    @property
    def name_l(self) -> str:
        sql_expression = self.parse_input_string(self.sql_dialect)

        base_name = add_suffix_to_all_column_identifiers(
            sql_expression, "_l", self.sql_dialect.sqlglot_name
        )
        return self.apply_operations(base_name, self.sql_dialect)

    @property
    def name_r(self) -> str:
        sql_expression = self.parse_input_string(self.sql_dialect)
        base_name = add_suffix_to_all_column_identifiers(
            sql_expression, "_r", self.sql_dialect.sqlglot_name
        )
        return self.apply_operations(base_name, self.sql_dialect)

    @property
    def l_name(self) -> str:
        sql_expression = self.parse_input_string(self.sql_dialect)
        base_name = add_table_to_all_column_identifiers(
            sql_expression, "l", self.sql_dialect.sqlglot_name
        )
        return self.apply_operations(base_name, self.sql_dialect)

    @property
    def r_name(self) -> str:
        sql_expression = self.parse_input_string(self.sql_dialect)
        base_name = add_table_to_all_column_identifiers(
            sql_expression, "r", self.sql_dialect.sqlglot_name
        )
        return self.apply_operations(base_name, self.sql_dialect)

    @property
    def output_column_name(self) -> str:
        allowed_chars = string.ascii_letters + string.digits + "_"
        sanitised_name = "".join(
            c if c in allowed_chars else "_" for c in self.raw_sql_expression
        )
        return sanitised_name

    @property
    def label(self) -> str:
        if len(self.operations) > 0:
            return "transformed " + self.raw_sql_expression
        else:
            return self.raw_sql_expression

    def __repr__(self):
        # TODO: need to include transform info, but guard for case of no dialect
        return f"ColumnExpression(sql_expression='{self.raw_sql_expression}')"
