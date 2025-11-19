import argparse
import pandas as pd
import polars as pl
import scipy.io
import gzip
import scanpy as sc
import anndata 

def read_gzip_tsv_polars(file_path):
    """Reads a gzipped TSV file into a Polars DataFrame."""
    with gzip.open(file_path, 'rb') as f:
        return pl.read_csv(f, separator='\t', has_header=False)

def clean_barcode_suffix(barcode):
    """Remove '-' and following numbers from cell barcode."""
    if '-' in barcode:
        return barcode.split('-')[0]
    return barcode

def process_input_files(matrix_path, barcodes_path, features_path, output_csv_path):
    # Load the input files
    print("Loading matrix.mtx.gz...")
    matrix = scipy.io.mmread(matrix_path).tocoo()  # Sparse COO format

    print("Loading barcodes.tsv.gz...")
    barcodes = read_gzip_tsv_polars(barcodes_path)
    
    print("Loading features.tsv.gz...")
    features = read_gzip_tsv_polars(features_path)
    
    barcodes_list = [clean_barcode_suffix(barcode) for barcode in barcodes.to_series().to_list()]
    print(f"Cleaned barcode suffixes. Example: {barcodes.to_series().to_list()[0]} -> {barcodes_list[0]}")
    features_list = features.to_series().to_list()

    data = {
        "CellId": [barcodes_list[j] for j in matrix.col],
        "GeneId": [features_list[i] for i in matrix.row],
        "Count": matrix.data
    }

    print(f"Processing {matrix.nnz} nonzero entries...")

    df = pl.DataFrame(data)

    print(f"Writing raw count matrix to {output_csv_path}...")
    df.write_csv(output_csv_path)

    # Normalize counts
    print("Normalizing counts...")

    # Reconstruct sparse matrix in CSC format (Scanpy prefers this)
    matrix = matrix.tocsc()

    adata = anndata.AnnData(X=matrix.transpose())
    adata.obs_names = barcodes_list
    adata.var_names = features_list

    sc.pp.normalize_total(adata, target_sum=1e4)
    normalized_matrix = adata.X.tocoo()

    # Extract normalized counts
    norm_data = []
    for i, j, value in zip(normalized_matrix.row, normalized_matrix.col, normalized_matrix.data):
        cell_id = adata.obs_names[i]
        gene_id = adata.var_names[j]
        norm_data.append([cell_id, gene_id, value])

    norm_df = pl.DataFrame(norm_data, schema=["CellId", "GeneId", "NormalizedCount"])
    normalized_output_csv_path = output_csv_path.replace(".csv", "_normalized.csv")

    print(f"Writing normalized count matrix to {normalized_output_csv_path}...")
    norm_df.write_csv(normalized_output_csv_path)

    print("Done!")

def main():
    parser = argparse.ArgumentParser(description="Convert .mtx.gz, .tsv.gz files into a count matrix CSV.")
    parser.add_argument('--matrix', required=True, help="Path to the matrix.mtx.gz file")
    parser.add_argument('--barcodes', required=True, help="Path to the barcodes.tsv.gz file")
    parser.add_argument('--features', required=True, help="Path to the features.tsv.gz file")
    parser.add_argument('--output', required=True, help="Path to output the raw CSV file")

    args = parser.parse_args()
    process_input_files(args.matrix, args.barcodes, args.features, args.output)

if __name__ == "__main__":
    main()
