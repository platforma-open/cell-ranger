---
"@platforma-open/milaboratories.cellranger.software": minor
"@platforma-open/milaboratories.cell-ranger.workflow": minor
"@platforma-open/milaboratories.cell-ranger.model": minor
"@platforma-open/milaboratories.cell-ranger.ui": minor
"@platforma-open/milaboratories.cell-ranger": minor
---

Fix the blank Cell Ranger Web Summary tab.

The summary is driven by inline scripts. It was rendered through an `iframe srcdoc`,
which inherits the Content-Security-Policy of the block UI document, and that policy
forbids inline scripts — so the panel came up empty.

The summary is now zipped by a new `pack-web-summary` software entrypoint and loaded
from the `plblob+folder://` URL that `extractArchiveAndGetURL` returns, giving it a
document of its own with no inherited policy. No CSP is relaxed anywhere.

Packing runs in `process.tpl.tengo` rather than in the hash-pinned
`cell-ranger.tpl.tengo`, so existing projects do not re-run the alignment.
