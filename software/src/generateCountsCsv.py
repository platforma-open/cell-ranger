import argparse
import pandas as pd
import scipy.io
import gzip

def read_gzip_tsv(file_path):
    """Reads a gzipped TSV file into a pandas DataFrame."""
    with gzip.open(file_path, 'rt') as f:
        return pd.read_csv(f, sep='\t', header=None)

def process_input_files(matrix_path, barcodes_path, features_path, output_csv_path):
    # Load the input files
    print("Loading matrix.mtx.gz...")
    matrix = scipy.io.mmread(matrix_path).tocoo()  # Read the matrix in sparse COO format

    print("Loading barcodes.tsv.gz...")
    barcodes = read_gzip_tsv(barcodes_path)
    
    print("Loading features.tsv.gz...")
    features = read_gzip_tsv(features_path)
    
    # Convert the barcodes and features to lists for easier reference
    barcodes_list = barcodes[0].tolist()  # Barcodes as list
    features_list = features[0].tolist()  # GeneIds as list

    # Prepare the data for output
    data = []
    
    # Iterate over the non-zero elements of the sparse matrix
    print(f"Processing {matrix.nnz} nonzero entries...")
    count_debug = 0  # Counter for how many entries are processed

    for i, j, value in zip(matrix.row, matrix.col, matrix.data):
        if count_debug < 10:  # Print only first 10 rows for debugging
            print(f"Row: {i}, Column: {j}, Count: {value}")

        cell_id = barcodes_list[j]  # Get cell ID from columns
        gene_id = features_list[i]  # Get gene ID from rows
        count = value  # The count (value in the matrix)

        data.append([cell_id, gene_id, count])
        count_debug += 1

    print(f"Total rows written: {count_debug}")
    
    # Create a DataFrame for easier manipulation
    df = pd.DataFrame(data, columns=["CellId", "GeneId", "Count"])

    # Write to CSV
    print(f"Writing to {output_csv_path}...")
    df.to_csv(output_csv_path, index=False)

    print("Done!")

def main():
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="Convert .mtx.gz, .tsv.gz files into a count matrix CSV.")
    parser.add_argument('--matrix', required=True, help="Path to the matrix.mtx.gz file")
    parser.add_argument('--barcodes', required=True, help="Path to the barcodes.tsv.gz file")
    parser.add_argument('--features', required=True, help="Path to the features.tsv.gz file")
    parser.add_argument('--output', required=True, help="Path to output the CSV file")
    
    # Parse the arguments
    args = parser.parse_args()

    # Call the function to process the files and generate the CSV
    process_input_files(args.matrix, args.barcodes, args.features, args.output)

if __name__ == "__main__":
    main()
