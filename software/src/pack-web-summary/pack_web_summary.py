import argparse
import os
import zipfile


def pack(input_path, output_path, entry_name):
    """
    Packs a single file into a zip archive.

    Args:
        input_path (str): Path to the file to pack.
        output_path (str): Path of the zip archive to write.
        entry_name (str): Name the file gets inside the archive.
    """
    size = os.path.getsize(input_path)
    # Cell Ranger's web summary is already a compressed-poorly single HTML blob;
    # ZIP_DEFLATED still roughly halves it at negligible cost.
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(input_path, arcname=entry_name)
    print(f"Packed {input_path} ({size} bytes) into {output_path} as {entry_name}")


def main():
    parser = argparse.ArgumentParser(
        description="Pack a single file into a zip archive."
    )
    parser.add_argument("--input", required=True, help="File to pack.")
    parser.add_argument("--output", required=True, help="Zip archive to write.")
    parser.add_argument(
        "--entry-name",
        required=True,
        help="Name the packed file gets inside the archive.",
    )
    args = parser.parse_args()
    pack(args.input, args.output, args.entry_name)


if __name__ == "__main__":
    main()
