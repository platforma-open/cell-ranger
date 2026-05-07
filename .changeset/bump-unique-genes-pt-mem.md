---
"@platforma-open/milaboratories.cell-ranger.workflow": patch
---

Bump the unique-Ensembl-Ids pt workflow from 4 GiB to 16 GiB. On large
datasets the polars-pf reader yielded batches up to ~17.5M rows before the
groupBy host process OOM'd at the previous 4 GiB ceiling. 16 GiB clears the
peak with headroom for polars' streaming-engine bookkeeping.
