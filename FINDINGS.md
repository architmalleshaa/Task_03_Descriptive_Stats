# Findings across election social media files

The three sources have distinct grains and schemas: 246,745 ads in 41 columns, 19,009 Facebook posts in 56 columns, and 27,304 Twitter posts in 47 columns. The same three scripts processed every file without code edits. Ad grouping uses page_id and page_id/ad_id; Facebook grouping uses Facebook_Id and post Type; Twitter grouping uses month_year and posting source. The Twitter CSV has no author/account identifier, so an account-level analysis would require data not provided.

Ads show concentrated estimated USD spending. The leading three literal funding bylines account for 51.16% of the $261,764,951 USD estimate. Estimates and foreign-currency rows are handled separately in the substantive narrative. All ad identifiers are unique, and ad-level groups therefore have undefined sample standard deviations. See `verified_results/ad_findings.json` for the ad-specific calculations.

Facebook posts span September 1, 2023 through November 6, 2024 and represent 21 distinct Facebook identifiers. Total Interactions has a mean of 4,190.44, median of 283 and maximum of 696,853. The much larger mean than median shows that unusually large observations affect the average. This is a descriptive result for the supplied records, not an estimate of all Facebook political engagement.

Twitter posts span September 1, 2023 through November 4, 2024. Likes average 6,913.69 with a median of 1,406; views average 507,084.73 with a median of 70,942 and a maximum of 333,502,775. These measures describe separate actions and must not be compared directly to Facebook Total Interactions as if they were identical metrics. The posting-source field describes the client or source label, not the identity of an account.

Quality varies across the files. Facebook has four entirely empty columns: Sponsor Id, Sponsor Name, Sponsor Category, and the merged header illuminating_scored_messageelection_integrity_Truth_illuminating. The latter is kept exactly as supplied. It is not split into two invented columns or used as evidence that election-integrity labels were negative. Several video fields have substantial missingness, which may reflect applicability as well as incomplete records. The file alone cannot distinguish those explanations.

Twitter has 1,270 missing observations in many annotation columns, including issue, attack and incivility. Those nulls are excluded from the relevant means; they are not changed to zeros. Facebook scam labels have 949 missing values. The shared-column table carries valid and missing denominators so a reader can see where coverage differs.

There are 27 literal column names common to all three files. All are recorded annotation indicators. Despite the assignment's illustrative reference to shared identifiers, dates and engagement, those exact fields are not universally shared in the actual files. The comparison therefore uses the verified annotation intersection, while reporting platform-specific engagement separately. `CROSS_DATASET.md` explains what the differences support and what they cannot establish.

Additional page-level result: the median page has 3 ads, while the largest page group has 55,503. These are counts of supplied ad records, not audience size or spending. The page groups sum to 246,745 rows.
