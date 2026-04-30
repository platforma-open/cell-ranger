import argparse
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

def process_input_files(matrix_path, barcodes_path, features_path, output_path):
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

    # Polars Series for vectorized lookup over nnz entries (no Python loop).
    cell_id_series = pl.Series(barcodes_list)
    gene_id_series = pl.Series(features_list)

    print(f"Processing {matrix.nnz} nonzero entries...")

    df = pl.DataFrame({
        "CellId": cell_id_series.gather(matrix.col),
        "GeneId": gene_id_series.gather(matrix.row),
        "Count": matrix.data,
    })

    print(f"Writing raw count matrix to {output_path}...")
    df.write_parquet(output_path)

    # Normalize counts
    print("Normalizing counts...")

    # Reconstruct sparse matrix in CSC format (Scanpy prefers this)
    matrix = matrix.tocsc()

    adata = anndata.AnnData(X=matrix.transpose())
    adata.obs_names = barcodes_list
    adata.var_names = features_list

    sc.pp.normalize_total(adata, target_sum=1e4)
    normalized_matrix = adata.X.tocoo()

    # Reuse the same Polars Series as above; scanpy doesn't reorder names.
    norm_df = pl.DataFrame({
        "CellId": cell_id_series.gather(normalized_matrix.row),
        "GeneId": gene_id_series.gather(normalized_matrix.col),
        "NormalizedCount": normalized_matrix.data,
    })
    normalized_output_path = output_path.replace(".parquet", "_normalized.parquet")

    print(f"Writing normalized count matrix to {normalized_output_path}...")
    norm_df.write_parquet(normalized_output_path)

    print("Done!")

def main():
    parser = argparse.ArgumentParser(description="Convert .mtx.gz, .tsv.gz files into raw and normalized count matrices in Parquet format.")
    parser.add_argument('--matrix', required=True, help="Path to the matrix.mtx.gz file")
    parser.add_argument('--barcodes', required=True, help="Path to the barcodes.tsv.gz file")
    parser.add_argument('--features', required=True, help="Path to the features.tsv.gz file")
    parser.add_argument('--output', required=True, help="Path to output the raw counts Parquet file")

    args = parser.parse_args()
    process_input_files(args.matrix, args.barcodes, args.features, args.output)

if __name__ == "__main__":
    main()
