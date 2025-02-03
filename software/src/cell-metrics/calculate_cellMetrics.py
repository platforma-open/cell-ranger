import scanpy as sc
import pandas as pd
import numpy as np
import argparse
import os
import scipy.sparse

def load_data(path):
    """ Load count data from a CSV file and convert to AnnData object """
    # Read CSV into a pandas DataFrame
    df = pd.read_csv(path)
    
    # Pivot the DataFrame to create a cell x gene matrix
    counts_matrix = df.pivot(index='CellId', columns='GeneId', values='Count').fillna(0)
    
    # Convert the DataFrame to a sparse matrix (fill missing values with 0)
    counts_matrix_sparse = scipy.sparse.csr_matrix(counts_matrix.values)
    
    # Create an AnnData object (cell x gene matrix)
    adata = sc.AnnData(counts_matrix_sparse)
    
    # Add gene names (column headers) and cell IDs (index) to adata.var and adata.obs respectively
    adata.var_names = counts_matrix.columns
    adata.obs_names = counts_matrix.index
    
    return adata

def calculate_metrics(adata):
    """ Calculate basic metrics: cell counts, UMIs per cell, genes detected per cell, and top 20 genes percentage """
    sc.pp.calculate_qc_metrics(adata, percent_top=[20], log1p=False, inplace=True)

def mitochondrial_percentage(adata, mito_genes_prefix):
    """ Calculate mitochondrial gene expression percentage """
    adata.var['mt'] = adata.var_names.str.startswith(mito_genes_prefix)  # mark mitochondrial genes
    # Calculate % mitochondrial genes
    adata.obs['pct_counts_mt'] = np.sum(
        adata[:, adata.var['mt']].X, axis=1).A1 / np.sum(adata.X, axis=1).A1 * 100

def compute_complexity(adata):
    """ Compute complexity or novelty score for each cell """
    adata.obs['complexity'] = adata.obs['n_genes_by_counts'] / adata.obs['total_counts']

def compute_mad_outliers(data, factor=5):
    """ Calculate outliers based on MAD (Median Absolute Deviation) """
    median = np.median(data)
    mad = np.median(np.abs(data - median))
    threshold_upper = median + factor * mad
    threshold_lower = median - factor * mad
    return (data > threshold_upper) | (data < threshold_lower)

def classify_outliers(adata, factors):
    """ Classify cells as outliers based on multiple metrics """
    outliers_total_counts = compute_mad_outliers(adata.obs['total_counts'], factor=factors['total_counts'])
    outliers_n_genes = compute_mad_outliers(adata.obs['n_genes_by_counts'], factor=factors['n_genes'])
    outliers_pct_top_20 = compute_mad_outliers(adata.obs['pct_counts_in_top_20_genes'], factor=factors['top_20_genes'])
    outliers_pct_mt = compute_mad_outliers(adata.obs['pct_counts_mt'], factor=factors['pct_mt'])

    # Combine all outlier indicators
    adata.obs['outlier'] = outliers_total_counts & outliers_n_genes & outliers_pct_top_20 & outliers_pct_mt

def export_metrics(adata, output_dir, filename="cell_metrics.csv"):
    """ Export metrics to a CSV file in the specified output directory """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    metrics_df = adata.obs[['total_counts', 'n_genes_by_counts', 'pct_counts_mt', 'complexity', 'pct_counts_in_top_20_genes', 'outlier']]
    metrics_df.index.name = 'CellId'
    metrics_df.reset_index().to_csv(output_path, index=False)

def get_mito_prefix(species):
    """ Return the mitochondrial gene prefix based on species """
    prefix_dict = {
        'saccharomyces-cerevisiae': 'MT-',
        'homo-sapiens': 'MT-',
        'mus-musculus': 'mt-',  # 'mt-' is more common for mouse datasets
        'rattus-norvegicus': 'MT-',
        'danio-rerio': 'mt-',  # 'mt-' is commonly used for zebrafish
        'drosophila-melanogaster': 'mt-',  # 'mt-' for Drosophila
        'arabidopsis-thaliana': 'ATMT-',  # Specific prefix for Arabidopsis
        'caenorhabditis-elegans': 'mt-',  # 'mt-' for C. elegans
        'gallus-gallus': 'MT-',  # 'MT-' for chicken
        'bos-taurus': 'MT-',  # 'MT-' for cattle
        'sus-scrofa': 'MT-'  # 'MT-' for pigs
    }
    return prefix_dict.get(species.lower(), 'MT-')  # Default to 'MT-' if species is unknown

def main():
    parser = argparse.ArgumentParser(description='Calculate cell metrics for single-cell RNA-seq data in CSV format.')
    parser.add_argument('--path', type=str, required=True, help='Path to the CSV file containing count data')
    parser.add_argument('--species', type=str, required=True, help='Species source of the data (e.g., homo-sapiens, mus-musculus, etc.)')
    parser.add_argument('--output', type=str, required=True, help='Output directory path where the CSV will be saved')
    
    args = parser.parse_args()
    
    # Load data
    adata = load_data(args.path)
    
    # Calculate metrics
    calculate_metrics(adata)
    
    # Determine mitochondrial gene prefix based on species and calculate mitochondrial percentage
    mito_prefix = get_mito_prefix(args.species)
    mitochondrial_percentage(adata, mito_prefix)
    
    # Compute complexity
    compute_complexity(adata)
    
    # Classify outliers based on MAD thresholds
    factors = {'total_counts': 5, 'n_genes': 5, 'top_20_genes': 5, 'pct_mt': 3}
    classify_outliers(adata, factors)
    
    # Export metrics to CSV
    export_metrics(adata, args.output)

if __name__ == "__main__":
    main()
