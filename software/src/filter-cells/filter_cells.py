import polars as pl
import argparse
import os


def filter_outliers(raw_counts_path, normalized_counts_path, metrics_path, output_raw_path, output_normalized_path):
    """
    Filters outlier cells from count matrices based on a metrics file.

    Args:
        raw_counts_path (str): Path to the raw counts Parquet file.
        normalized_counts_path (str): Path to the normalized counts Parquet file.
        metrics_path (str): Path to the cell metrics CSV file containing outlier flags.
        output_raw_path (str): Path to save the filtered raw counts Parquet file.
        output_normalized_path (str): Path to save the filtered normalized counts Parquet file.
    """
    # Metrics is small (one row per cell); fine to load eagerly.
    metrics_df = pl.read_csv(metrics_path)
    outliers_df = metrics_df.filter(pl.col('outlier'))
    outlier_cells_lf = outliers_df.select('CellId').lazy()

    initial_cell_count = metrics_df.height
    outlier_cell_count = outliers_df.height
    print(f"Total number of cells: {initial_cell_count}")
    print(f"Number of cells flagged as outliers: {outlier_cell_count}")
    print(f"Number of cells after filtering: {initial_cell_count - outlier_cell_count}")

    # Resolve output paths before sinking.
    if os.path.isdir(output_raw_path):
        output_raw_path = os.path.join(output_raw_path, 'filtered_raw_counts.parquet')
    if os.path.isdir(output_normalized_path):
        output_normalized_path = os.path.join(output_normalized_path, 'filtered_normalized_counts.parquet')

    # Stream the long-format counts: scan + lazy anti-join + sink, no full
    # materialization of either count file.
    pl.scan_parquet(raw_counts_path) \
        .join(outlier_cells_lf, on='CellId', how='anti') \
        .sink_parquet(output_raw_path)
    pl.scan_parquet(normalized_counts_path) \
        .join(outlier_cells_lf, on='CellId', how='anti') \
        .sink_parquet(output_normalized_path)

def main():
    parser = argparse.ArgumentParser(description='Filter outlier cells from count matrices.')
    parser.add_argument('--raw_counts', type=str, required=True, help='Path to raw counts Parquet file.')
    parser.add_argument('--normalized_counts', type=str, required=True, help='Path to normalized counts Parquet file.')
    parser.add_argument('--metrics', type=str, required=True, help='Path to cell metrics CSV file.')
    parser.add_argument('--output_raw', type=str, required=True, help='Path to save filtered raw counts Parquet file.')
    parser.add_argument('--output_normalized', type=str, required=True, help='Path to save filtered normalized counts Parquet file.')

    args = parser.parse_args()

    filter_outliers(args.raw_counts, args.normalized_counts, args.metrics, args.output_raw, args.output_normalized)

if __name__ == "__main__":
    main()