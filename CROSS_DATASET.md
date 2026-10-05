# Comparing shared fields

The verified intersection contains 27 annotation columns. The full list, valid counts, missing counts and means appears in [SHARED_COLUMNS.md](verified_results/comparison/SHARED_COLUMNS.md); [shared_column_statistics.json](verified_results/comparison/shared_column_statistics.json) also contains every required numeric statistic for each shared field. The accompanying `cross_dataset.py` generates both directly from the engine summaries.

| Recorded label | Ads positive | Facebook posts positive | Twitter posts positive |
|---|---:|---:|---:|
| Issue | 38.16% | 46.03% | 50.77% |
| Attack | 27.19% | 21.67% | 30.76% |
| Fundraising call to action | 22.85% | 1.84% | 0.79% |
| Incivility | 18.75% | 12.79% | 17.86% |

Each percentage is the mean of a binary annotation among non-missing observations. Denominators for these four labels are 246,745 ads, 19,009 Facebook posts and 26,034 Twitter posts. Twitter's remaining 1,270 records have missing labels. The comparison describes assigned labels, not verified intent or content accuracy.

The largest contrast in this selection is the fundraising label: it is much more common in the ads file. That is consistent with different purposes for paid and organic content, but the files cannot establish that explanation. Differences in sampled organizations, observation dates, repeated messages, label generation or missingness could also matter. A platform effect is not identified.

Coverage is not identical. Ads have creation dates from 2021-07-06 through 2024-11-05; Facebook posts cover 2023-09-01 through 2024-11-06; Twitter posts cover 2023-09-01 through 2024-11-04. The table uses each supplied file in full rather than silently presenting it as a matched-period panel. No cross-platform user or organization join is attempted: identifiers are not interchangeable, and Twitter has no account key.

Views, likes, interactions and paid impressions are kept separate. They have different definitions and exposure processes. Similarly, the all-empty merged Facebook header does not count as a matching election_integrity_Truth_illuminating field. The common-column intersection follows actual headers rather than the task's illustrative examples.

These data support a descriptive comparison of observed annotation distributions. They do not support claims that one platform causes more attack content, that a campaign's true spending equals an interval midpoint, or that engagement counts measure unique persuaded voters.
