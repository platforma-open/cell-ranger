# Overview

Processes single-cell RNA sequencing raw data generated using Chromium platform from 10x Genomics. The block performs alignment, quantification, quality control (QC) metric calculation, and cell filtering to generate high-quality count matrices suitable for downstream analysis.

The block uses Cell Ranger to align sequencing reads to a reference genome and quantify gene expression. For each cell, comprehensive quality control metrics are calculated, including the total number of RNA molecules detected, the number of unique genes expressed, the percentage of counts from mitochondrial genes (with species-specific prefix detection), a complexity score representing the ratio of detected genes to total counts, and the percentage of counts in the top 20 most highly expressed genes. These metrics help identify cells with potential issues such as low sequencing depth, cell death, or technical artifacts.

Cells are filtered using a robust outlier detection method based on Median Absolute Deviation (MAD). The method applies configurable thresholds to identify outliers: 5× MAD for total counts, number of genes, and top 20 genes percentage, and 3× MAD for mitochondrial percentage. Importantly, a cell is only flagged as an outlier and removed if it exceeds thresholds in **all four metrics** simultaneously. This conservative approach ensures that only cells with multiple quality issues are filtered, preserving cells that may have a single metric outside the normal range but are otherwise of good quality.

The filtered raw and normalized count matrices can then be used in downstream blocks for deeper analysis, such as dimensionality reduction, clustering, differential expression analysis, or cell type annotation.

Cell Ranger is developed by 10x Genomics. For more information, please see the [10x Genomics website](https://www.10xgenomics.com/). When using this block in your research, cite the software as **10x Genomics Cell Ranger v9.0.0**.

The following publication describes the methodology:

> Zheng, G. X. Y., Terry, J. M., Belgrader, P. et al. Massively parallel digital transcriptional profiling of single cells. _Nat Commun_ **8**, 14049 (2017) [https://doi.org/10.1038/ncomms14049](https://doi.org/10.1038/ncomms14049)
