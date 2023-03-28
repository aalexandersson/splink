---
tags:
  - API
  - comparisons
  - Levenshtein
  - Jaro-Winkler
  - Jaccard
  - Date Difference
  - Distance In KM
  - Array Intersect
  - Columns Reversed
  - Percentage Difference
---
# Documentation for `comparison_level_library` 

The `comparison_level_library` contains pre-made comparison levels available for use to
construct custom comparisons [as described in this topic guide](./topic_guides/customising_comparisons.html#method-3-comparisonlevels).
However, not every comparison level is available for every [Splink-compatible SQL backend](./topic_guides/backends.html).

The pre-made Splink comparison levels available for each SQL dialect are as given in this table:

{% include-markdown "./includes/generated_files/comparison_level_library_dialect_table.md" %}



The detailed API for each of these are outlined below.

## Library comparison level APIs

::: splink.comparison_level_library.NullLevelBase
    handler: python
    selection:
      members:
        -  __init__
    rendering:
      show_root_heading: true
      show_source: false
      heading_level: 2

---

::: splink.comparison_level_library.ExactMatchLevelBase
    handler: python
    selection:
      members:
        -  __init__
    rendering:
      show_root_heading: true
      show_source: false
      heading_level: 2
      
---

::: splink.comparison_level_library.ElseLevelBase
    handler: python
    selection:
      members:
        -  __init__
    rendering:
      show_root_heading: true
      show_source: false
      heading_level: 2

---

::: splink.comparison_level_library.DistanceFunctionLevelBase
    handler: python
    selection:
      members:
        -  __init__
    rendering:
      show_root_heading: true
      show_source: false
      heading_level: 2

---

::: splink.comparison_level_library.LevenshteinLevelBase
    handler: python
    selection:
      members:
        -  __init__
    rendering:
      show_root_heading: true
      show_source: false   
      heading_level: 2

---

::: splink.comparison_level_library.JaroWinklerLevelBase
    handler: python
    selection:
      members:
        -  __init__
    rendering:
      show_root_heading: true
      show_source: false
      heading_level: 2

---

::: splink.comparison_level_library.JaccardLevelBase
    handler: python
    selection:
      members:
        -  __init__
    rendering:
      show_root_heading: true
      show_source: false
      heading_level: 2

---

::: splink.comparison_level_library.ColumnsReversedLevelBase
    handler: python
    selection:
      members:
        -  __init__
    rendering:
      show_root_heading: true
      show_source: false
      heading_level: 2

---

::: splink.comparison_level_library.DistanceInKMLevelBase
    handler: python
    selection:
      members:
        -  __init__
    rendering:
      show_root_heading: true
      show_source: false
      heading_level: 2    

---

::: splink.comparison_level_library.PercentageDifferenceLevelBase
    handler: python
    selection:
      members:
        -  __init__
    rendering:
      show_root_heading: true
      show_source: false
      heading_level: 2   

---

::: splink.comparison_level_library.ArrayIntersectLevelBase
    handler: python
    selection:
      members:
        -  __init__
    rendering:
      show_root_heading: true
      show_source: false
      heading_level: 2

---

::: splink.comparison_level_library.DateDiffLevelBase
    handler: python
    selection:
      members:
        -  __init__
    rendering:
      show_root_heading: true
      show_source: false
      heading_level: 2
