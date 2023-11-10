from typing import Union

from .comparison_level_creator import ComparisonLevelCreator
from .dialects import SplinkDialect
from .comparison_level_extenders import regex_extract_col, lowercase_col


class NullLevel(ComparisonLevelCreator):
    def create_sql(self, sql_dialect: SplinkDialect) -> str:
        col = self.input_column(sql_dialect)
        return f"{col.name_l()} IS NULL OR {col.name_r()} IS NULL"

    def create_label_for_charts(self) -> str:
        return f"{self.col_name} is NULL"


class ElseLevel(ComparisonLevelCreator):
    def create_sql(self, sql_dialect: SplinkDialect) -> str:
        return "ELSE"

    def create_label_for_charts(self) -> str:
        return "All other comparisons"


@regex_extract_col
@lowercase_col
class ExactMatchLevel(ComparisonLevelCreator):
    def __init__(
        self,
        col_name: str,
        term_frequency_adjustments: bool = False,
        regex_extract: str = None,
        set_to_lowercase: bool = False,
    ):
        """Represents a comparison level where there is an exact match

        e.g. val_l = val_r

        Args:
            col_name (str): Input column name
            term_frequency_adjustments (bool, optional): If True, apply term frequency
                adjustments to the exact match level. Defaults to False.

        """

        self._regex_extract_str = regex_extract
        self._set_to_lowercase = set_to_lowercase

        config = {}
        if term_frequency_adjustments:
            config["tf_adjustment_column"] = col_name
            config["tf_adjustment_weight"] = 1.0
            # leave tf_minimum_u_value as None
        super().__init__(col_name)
        self.configure(**config)

    def create_sql(self, sql_dialect: SplinkDialect) -> str:
        col_l, col_r = self.cols_l_r(sql_dialect)
        return f"{col_l} = {col_r}"

    def create_label_for_charts(self) -> str:
        return f"Exact match on {self.col_name}"


class LevenshteinLevel(ComparisonLevelCreator):
    def __init__(self, col_name: str, distance_threshold: int):
        """A comparison level using a levenshtein distance function

        e.g. levenshtein(val_l, val_r) <= distance_threshold

        Args:
            col_name (str): Input column name
            distance_threshold (int): The threshold to use to assess
                similarity
        """
        super().__init__(col_name)
        self.distance_threshold = distance_threshold

    def create_sql(self, sql_dialect: SplinkDialect) -> str:
        col = self.input_column(sql_dialect)
        lev_fn = sql_dialect.levenshtein_function_name
        return f"{lev_fn}({col.name_l()}, {col.name_r()}) <= {self.distance_threshold}"

    def create_label_for_charts(self) -> str:
        return f"Levenshtein distance of {self.col_name} <= {self.distance_threshold}"


class JaroWinklerLevel(ComparisonLevelCreator):
    def __init__(self, col_name: str, distance_threshold: Union[int, float]):
        """A comparison level using a Jaro-Winkler distance function

        e.g. `jaro_winkler(val_l, val_r) >= distance_threshold`

        Args:
            col_name (str): Input column name
            distance_threshold (Union[int, float]): The threshold to use to assess
                similarity
        """
        super().__init__(col_name)
        self.distance_threshold = distance_threshold

    def create_sql(self, sql_dialect: SplinkDialect) -> str:
        col_l, col_r = self.input_column(sql_dialect).names_l_r()
        jw_fn = sql_dialect.jaro_winkler_function_name
        return f"{jw_fn}({col_l}, {col_r}) >= {self.distance_threshold}"

    def create_label_for_charts(self) -> str:
        return (
            f"Jaro-Winkler distance of '{self.col_name} >= {self.distance_threshold}'"
        )
