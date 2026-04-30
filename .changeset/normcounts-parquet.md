---
"@platforma-open/milaboratories.cellranger.software": patch
"@platforma-open/milaboratories.cell-ranger.workflow": patch
"@platforma-open/milaboratories.cell-ranger": patch
---

Emit raw and normalized count matrices as Parquet instead of CSV. Set
explicit `mem: "16GiB"` / `cpu: 2` on the `rawCounts` and `normCounts`
Xsv outputs so the auto-import ptabler container has enough headroom
for large scRNA-seq matrices. Mitigates ptabler "exit code 50002"
failures during the CSV→Parquet conversion of `normCounts`.
