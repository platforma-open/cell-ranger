---
"@platforma-open/milaboratories.cellranger.software": patch
"@platforma-open/milaboratories.cell-ranger.workflow": patch
"@platforma-open/milaboratories.cell-ranger": patch
---

Rebuild the Docker images of the Python software on the current python:3.12-slim. The new base image does not trust the compromised eMudhra intermediate CAs. Remove the unused calculate-hvg Dockerfile.
