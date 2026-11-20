# Chaining vs. linear probing

Capacity: 1000; same deterministic key set at each load factor; 900 unsuccessful queries per row.

| α | n | Chain hit (obs/theory) | Chain miss (obs/theory) | Linear hit (obs/theory) | Linear miss (obs/theory) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.1 | 100 | 1.030/1.050 | 0.093/0.100 | 1.030/1.056 | 1.120/1.117 |
| 0.2 | 200 | 1.055/1.100 | 0.200/0.200 | 1.065/1.125 | 1.274/1.281 |
| 0.3 | 300 | 1.113/1.150 | 0.302/0.300 | 1.153/1.214 | 1.493/1.520 |
| 0.4 | 400 | 1.157/1.200 | 0.394/0.400 | 1.260/1.333 | 1.806/1.889 |
| 0.5 | 500 | 1.196/1.250 | 0.482/0.500 | 1.354/1.500 | 2.198/2.500 |
| 0.6 | 600 | 1.250/1.300 | 0.587/0.600 | 1.590/1.750 | 3.219/3.625 |
| 0.7 | 700 | 1.287/1.350 | 0.700/0.700 | 2.081/2.167 | 5.029/6.056 |
| 0.8 | 800 | 1.333/1.400 | 0.793/0.800 | 2.815/3.000 | 10.152/13.000 |
| 0.9 | 900 | 1.391/1.450 | 0.891/0.900 | 4.513/5.500 | 39.877/50.500 |

Chaining theory: successful `1 + α/2`, unsuccessful `α`. Linear-probing theory: successful `0.5(1 + 1/(1-α))`, unsuccessful `0.5(1 + 1/(1-α)^2)`.

The linear-probing estimates rise sharply near full capacity because contiguous occupied runs cause primary clustering. Chaining grows more gradually; finite deterministic keys and discrete bucket occupancy explain small departures from the idealized uniform-hashing estimates.
