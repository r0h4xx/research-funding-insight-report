# Research funding and the research training pipeline in Australian universities

Insight report linking the Australian Government Department of Education's Higher Education Statistics
with Research Block Grant (RBG) allocations. Author: Roha Sohaib.

## Findings
1. At the same number of higher degree by research (HDR) completions, Group of Eight universities receive
   about 1.5 times the Research Training Program (RTP) funding of other universities (2023–2026 allocations).
2. Overseas students made up half of new HDR students in 2024, up from 35% in 2020, as domestic HDR
   commencements fell 19.9%.

## Data 
| File | Source |
|---|---|
| `Research_block_grants_time_series_2021-2026.xlsx` | https://www.education.gov.au/research-block-grants/resources/research-block-grant-allocations-time-series |
| `Perturbed_Award_Course_Completions_Pivot_Table_2024.xlsx` | https://www.education.gov.au/higher-education-statistics (2024 Student data, Award Course Completions Pivot Table) |
| `Perturbed_Student_Enrolments_Pivot_Table_2024.xlsx` | https://www.education.gov.au/higher-education-statistics (2024 Student data, Student Enrolment Pivot Table) |

The pivot workbooks show only a summary on their visible sheets. The full record set (98,800 completion rows and
235,292 enrolment rows, 2020–2024) sits in each workbook's pivot cache, which `extract_pivot_cache.py` reads.

## Method notes
- **Name crosswalk (student data -> RBG):** CQUniversity to Central Queensland University; RMIT University to Royal Melbourne Institute of Technology; The University of New England to  University of New England;
  The University of Newcastle to University of Newcastle.
- **Time alignment:** allocation year N is paired with mean HDR completions in N-3 and N-2. All four possible alignments in the data are tested.
- **Merger:** Adelaide University (2026) is compared with the combined University of Adelaide and UniSA.
  Group-share trends stop at 2025.
- **Model:** OLS of log(RTP) on log(HDR completions) plus a Go8 indicator. 39 universities with at least 20 completions a year.
- **Limitations:** research income (half the RTP formula) is not in these datasets. Completions are unweighted and perturbed. Dollars are nominal. The analysis is descriptive.
