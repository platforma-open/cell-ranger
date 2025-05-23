import pandas as pd
import argparse

def map_ensembl_to_gene_symbol(raw_counts_path, annotation_path, output_path):
    # Load the raw count data
    print("Loading raw count data...")
    raw_df = pd.read_csv(raw_counts_path)

    # Validate required columns in raw count data
    expected_columns = {"Sample", "Cell Barcode", "Ensembl Id", "Raw gene expression"}
    if not expected_columns.issubset(raw_df.columns):
        raise ValueError(f"Raw count data must contain columns: {expected_columns}")

    # Extract unique Ensembl IDs
    unique_ensembl_ids = raw_df["Ensembl Id"].unique()
    print(f"Found {len(unique_ensembl_ids)} unique Ensembl IDs.")

    # Load the annotation data
    print("Loading annotation data...")
    annotation_df = pd.read_csv(annotation_path)

    # Validate required columns in annotation data
    if not {"Ensembl Id", "Gene symbol"}.issubset(annotation_df.columns):
        raise ValueError("Annotation file must contain 'Ensembl Id' and 'Gene symbol' columns")

    # Create a mapping dictionary from the annotation file
    annotation_map = annotation_df.drop_duplicates("Ensembl Id").set_index("Ensembl Id")

    # Map Ensembl IDs to Gene symbols
    print("Mapping Ensembl IDs to gene symbols...")
    mapped_df = pd.DataFrame(unique_ensembl_ids, columns=["Ensembl Id"])
    mapped_df["Gene symbol"] = mapped_df["Ensembl Id"].map(annotation_map["Gene symbol"])

    # Report missing mappings
    missing = mapped_df["Gene symbol"].isnull().sum()
    print(f"Mapping complete. {missing} Ensembl IDs could not be mapped to gene symbols.")

    # Save output
    print(f"Saving output to {output_path}...")
    mapped_df.to_csv(output_path, index=False)
    print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Map Ensembl IDs in single-cell RNA-seq count data to gene symbols.")
    parser.add_argument("--raw_counts", required=True, help="Path to raw count CSV file")
    parser.add_argument("--annotation", required=True, help="Path to annotation CSV file (e.g. mus_musculus_gene_annotations.csv)")
    parser.add_argument("--output", required=True, help="Path to output CSV file with Ensembl Id and Gene symbol")

    args = parser.parse_args()
    map_ensembl_to_gene_symbol(args.raw_counts, args.annotation, args.output)
