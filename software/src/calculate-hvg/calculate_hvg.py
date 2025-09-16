# polars_hvg_selector.py

import polars as pl
import pandas as pd
import anndata
import scanpy as sc
import numpy as np
import os
import argparse
import pyarrow
from scipy.sparse import coo_matrix

def select_dynamic_hvgs_polars(raw_input_path, normalized_input_path, raw_output_path, normalized_output_path, max_rows=5000000, max_genes_cap=10000):
    """
    Selects highly variable genes (HVGs) from single-cell count matrices using Polars.

    HVG selection is performed on the raw counts file. The resulting list of HVGs
    is then used to filter both the raw and normalized count matrices.

    Args:
        raw_input_path (str): Path to the raw counts CSV file.
                              Expected format: Sample, Cell ID, Ensembl Id, Raw gene expression.
        normalized_input_path (str): Path to the normalized counts CSV file.
        raw_output_path (str): Path to save the filtered raw counts CSV file.
        normalized_output_path (str): Path to save the filtered normalized counts CSV file.
        max_rows (int): The maximum number of rows for the output CSV. Defaults to 8,000,000.
        max_genes_cap (int): A safeguard to prevent selecting an unrealistically large
                             number of genes. Defaults to 10000.
    """
    for path in [raw_input_path, normalized_input_path]:
        if not os.path.exists(path):
            print(f"Error: Input file not found at '{path}'")
            return

    print("Step 1: Reading and parsing input data with Polars...")
    try:
        # Read the raw and normalized data with Polars
        df_pl = pl.read_csv(raw_input_path)
        df_normalized_pl = pl.read_csv(normalized_input_path)
    except Exception as e:
        print(f"Error reading CSV file with Polars: {e}")
        return

    # Check for required columns
    required_raw_cols = {'Sample', 'Cell ID', 'Ensembl Id', 'Raw gene expression'}
    required_norm_cols = {'Sample', 'Cell ID', 'Ensembl Id'} # Value column can vary
    if not required_raw_cols.issubset(df_pl.columns):
        print(f"Error: Raw input CSV must contain columns: {list(required_raw_cols)}")
        return
    if not required_norm_cols.issubset(df_normalized_pl.columns):
        print(f"Error: Normalized input CSV must contain at least: {list(required_norm_cols)}")
        return

    print("Step 2: Creating a sparse matrix and preparing for HVG analysis...")

    # Get unique cell and gene IDs to define the dimensions of our matrix
    cell_ids = df_pl.get_column('Cell ID').unique().to_list()
    gene_ids = df_pl.get_column('Ensembl Id').unique().to_list()

    # Create mapping DataFrames from IDs to integer indices
    cell_map_df = pl.DataFrame({'Cell ID': cell_ids, 'row_idx': np.arange(len(cell_ids))})
    gene_map_df = pl.DataFrame({'Ensembl Id': gene_ids, 'col_idx': np.arange(len(gene_ids))})

    # Join the mapping DataFrames onto the original DataFrame to get indices
    df_with_indices = df_pl.join(cell_map_df, on='Cell ID', how='left').join(gene_map_df, on='Ensembl Id', how='left')
    
    # Extract the row and column indices and the data for the sparse matrix
    row_indices = df_with_indices.get_column('row_idx')
    col_indices = df_with_indices.get_column('col_idx')
    data = df_with_indices.get_column('Raw gene expression')

    # Create a sparse matrix in COO format, then convert to CSR for efficiency
    sparse_matrix = coo_matrix(
        (data, (row_indices, col_indices)),
        shape=(len(cell_ids), len(gene_ids))
    ).tocsr()

    # Create the AnnData object using the sparse matrix
    adata = anndata.AnnData(
        X=sparse_matrix,
        obs=pd.DataFrame(index=cell_ids),
        var=pd.DataFrame(index=gene_ids)
    )

    print("Step 3a: Pre-filtering data based on cell counts...")
    print(f"Original number of genes: {adata.n_vars}")
    # Filter genes that are expressed in a very small number of cells
    sc.pp.filter_genes(adata, min_cells=3)
    print(f"Number of genes after filtering: {adata.n_vars}")

    # Check if we have enough genes left to run the analysis
    if adata.n_vars < 3:
        print("Error: Too few genes remaining after filtering to perform HVG analysis.")
        print("This dataset may not be suitable for this analysis, or filtering parameters may be too strict.")
        return

    print("Step 3b: Running Highly Variable Gene (HVG) analysis on filtered genes...")
    # Run HVG analysis on all genes to get their ranks
    try:
        sc.pp.highly_variable_genes(adata, n_top_genes=max_genes_cap, flavor='seurat_v3', subset=False)
    except ValueError as e:
        if 'reciprocal condition number' in str(e):
            print("Error: HVG analysis failed likely due to numerical instability.")
            print("This can happen with datasets that have low numbers of genes or low expression variance.")
            print("Please inspect your input data. The number of genes after filtering was:", adata.n_vars)
            return
        else:
            raise e
    
    # Get a DataFrame of genes sorted by their variability rank
    ranked_genes_pd = adata.var.sort_values('highly_variable_rank')
    ranked_genes_pd = ranked_genes_pd[ranked_genes_pd['highly_variable'] == True]

    print("Step 4: Counting rows per gene in the original data...")
    # Use Polars to efficiently count the number of rows each gene contributes
    gene_row_counts_pl = df_pl.group_by("Ensembl Id").len()
    
    # Create a dictionary for fast lookups: {gene_id: row_count}
    gene_row_counts_dict = {
        row['Ensembl Id']: row['len'] 
        for row in gene_row_counts_pl.iter_rows(named=True)
    }

    print(f"Step 5: Iteratively selecting top HVGs to stay under {max_rows} rows...")
    hvg_list = []
    cumulative_rows = 0
    
    # Iterate through the ranked genes and add them until a limit is reached
    for gene_id in ranked_genes_pd.index:
        rows_for_this_gene = gene_row_counts_dict.get(gene_id, 0)
        
        # Stop if adding the next gene would exceed either the row limit or the gene cap
        if (cumulative_rows + rows_for_this_gene > max_rows):
            break
            
        hvg_list.append(gene_id)
        cumulative_rows += rows_for_this_gene

    print(f"Step 6: Selected {len(hvg_list)} HVGs, resulting in {cumulative_rows} total rows.")
    print("Step 7: Filtering original raw and normalized data...")
    
    # Filter the original Polars DataFrame using the iteratively built list of HVGs
    df_raw_filtered = df_pl.filter(pl.col("Ensembl Id").is_in(hvg_list))
    df_normalized_filtered = df_normalized_pl.filter(pl.col("Ensembl Id").is_in(hvg_list))
    
    # Sanity check on the final number of rows
    final_rows = df_raw_filtered.height
    print(f"Step 8: Final CSVs will have {final_rows} rows.")

    # Save the filtered DataFrame to a new CSV file
    df_raw_filtered.write_csv(raw_output_path)
    df_normalized_filtered.write_csv(normalized_output_path)
    print(f"Success! Filtered raw counts saved to '{raw_output_path}'.")
    print(f"Success! Filtered normalized counts saved to '{normalized_output_path}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Selects Highly Variable Genes (HVGs) from raw and normalized single-cell count matrices.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--raw_input', type=str, required=True, 
                        help='Path to the input raw counts CSV file.')
    parser.add_argument('--normalized_input', type=str, required=True,
                        help='Path to the input normalized counts CSV file.')
    parser.add_argument('--output_raw', type=str, required=True, 
                        help='Path to save the filtered raw counts output CSV file.')
    parser.add_argument('--output_normalized', type=str, required=True,
                        help='Path to save the filtered normalized counts output CSV file.')
    parser.add_argument('--max_rows', type=int, default=5000000, 
                        help='The target maximum number of rows for the output CSV.')
    parser.add_argument('--max_genes_cap', type=int, default=10000, 
                        help='A safeguard cap on the number of genes to select.')
    
    args = parser.parse_args()
    
    select_dynamic_hvgs_polars(
        args.raw_input, 
        args.normalized_input,
        args.output_raw, 
        args.output_normalized,
        args.max_rows, 
        args.max_genes_cap
    )