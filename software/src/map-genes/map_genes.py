import polars as pl
import argparse


def map_ensembl_to_gene_symbol(raw_counts_path, annotation_path, output_path):
    # Lazily load the raw count data to select columns before parsing
    print("Loading raw count data...")
    try:
        raw_lazy = pl.scan_csv(raw_counts_path)
        raw_df = raw_lazy.select(["Ensembl Id"]).collect()
    except pl.ColumnNotFoundError:
        raise ValueError("Raw count data must contain 'Ensembl Id' column")

    # Extract unique Ensembl IDs
    unique_ensembl_ids = raw_df["Ensembl Id"].unique()
    print(f"Found {len(unique_ensembl_ids)} unique Ensembl IDs.")

    # Lazily load the annotation data
    print("Loading annotation data...")
    try:
        annotation_lazy = pl.scan_csv(annotation_path)
        annotation_df = annotation_lazy.select(["Ensembl Id", "Gene symbol"]).collect()
    except pl.ColumnNotFoundError:
        raise ValueError("Annotation file must contain 'Ensembl Id' and 'Gene symbol' columns")

    # Create a mapping DataFrame from the annotation file
    annotation_map = annotation_df.unique(subset=["Ensembl Id"])

    # Map Ensembl IDs to Gene symbols using a join
    print("Mapping Ensembl IDs to gene symbols...")
    mapped_df = pl.DataFrame({"Ensembl Id": unique_ensembl_ids})
    mapped_df = mapped_df.join(annotation_map, on="Ensembl Id", how="left")

    # Report missing mappings
    missing = mapped_df["Gene symbol"].is_null().sum()
    print(f"Mapping complete. {missing} Ensembl IDs could not be mapped to gene symbols.")

    # Add Ensembl ID as label when gene symbol is missing
    mapped_df = mapped_df.with_columns(
        pl.when(pl.col("Gene symbol").is_null())
        .then(pl.col("Ensembl Id"))
        .otherwise(pl.col("Gene symbol"))
        .alias("Gene symbol")
    )

    # Save output
    print(f"Saving output to {output_path}...")
    mapped_df.write_csv(output_path)
    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Map Ensembl IDs in single-cell RNA-seq count data to gene symbols.")
    parser.add_argument("--raw_counts", required=True, help="Path to raw count CSV file")
    parser.add_argument("--annotation", required=True, help="Path to annotation CSV file (e.g. mus_musculus_gene_annotations.csv)")
    parser.add_argument("--output", required=True, help="Path to output CSV file with Ensembl Id and Gene symbol")

    args = parser.parse_args()
    map_ensembl_to_gene_symbol(args.raw_counts, args.annotation, args.output)
