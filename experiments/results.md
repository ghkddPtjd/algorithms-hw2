# Separate-chaining lookup comparisons

Capacity: 4093; deterministic random URLs; 16372 unsuccessful queries per load factor.

Target load factors run from 0.25 to 4.00 in 0.25 steps. Entry counts are rounded to integers, and theory uses the resulting actual load factor.

| Target α | Actual α | Entries | Successful: measured | Successful: theory | Failed: measured | Failed: theory |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.25 | 0.2499 | 1023 | 1.126 | 1.125 | 0.247 | 0.250 |
| 0.50 | 0.4999 | 2046 | 1.242 | 1.250 | 0.497 | 0.500 |
| 0.75 | 0.7501 | 3070 | 1.356 | 1.375 | 0.752 | 0.750 |
| 1.00 | 1.0000 | 4093 | 1.482 | 1.500 | 1.001 | 1.000 |
| 1.25 | 1.2499 | 5116 | 1.601 | 1.625 | 1.248 | 1.250 |
| 1.50 | 1.5001 | 6140 | 1.729 | 1.750 | 1.493 | 1.500 |
| 1.75 | 1.7501 | 7163 | 1.854 | 1.875 | 1.744 | 1.750 |
| 2.00 | 2.0000 | 8186 | 1.971 | 2.000 | 1.998 | 2.000 |
| 2.25 | 2.2499 | 9209 | 2.099 | 2.125 | 2.246 | 2.250 |
| 2.50 | 2.4999 | 10232 | 2.224 | 2.250 | 2.495 | 2.500 |
| 2.75 | 2.7501 | 11256 | 2.351 | 2.375 | 2.747 | 2.750 |
| 3.00 | 3.0000 | 12279 | 2.481 | 2.500 | 2.996 | 3.000 |
| 3.25 | 3.2499 | 13302 | 2.609 | 2.625 | 3.251 | 3.250 |
| 3.50 | 3.5001 | 14326 | 2.731 | 2.750 | 3.499 | 3.500 |
| 3.75 | 3.7501 | 15349 | 2.856 | 2.875 | 3.745 | 3.750 |
| 4.00 | 4.0000 | 16372 | 2.983 | 3.000 | 3.991 | 4.000 |

The theoretical estimates are `1 + α/2` for successful search and `α` for unsuccessful search.
