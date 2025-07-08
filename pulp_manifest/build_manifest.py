import argparse
import fnmatch
import os
import sys
from urllib.parse import urlparse
from hashlib import sha256


def write_manifest(file_path, manifest_lines):
    """
    Write the manifest lines to the specified file path.

    :param file_path: str, path to the file where the manifest will be written
    :param manifest_lines: list of str, lines to write to the manifest file
    """
    with open(file_path, "w", encoding="utf-8") as fp:
        for line in manifest_lines:
            fp.write(line + "\n")


def get_digest(path):
    """
    Get the sha256 digest of the file at path.

    :param path: str of the file path that we need the digest for
    :return: str that is the file digest
    """
    digest = sha256()
    with open(path, "rb") as fp:
        digest.update(fp.read())
    return digest.hexdigest()


def traverse_dir(directory, exclude=None):
    """
    Traverse a given directory path and generate the PULP_MANIFEST
    associated with it.

    :param directory: str
    :param exclude: str, optional glob pattern to exclude files or directories
    :return: list of pulp manifest items
    """
    manifest = []
    for root, dirs, files in os.walk(directory, followlinks=True):
        for file in files:
            if exclude and fnmatch.fnmatch(file, f"*{exclude}*"):
                continue
            file_path = os.path.join(root, file)
            line = []

            line.append(os.path.relpath(file_path, directory))
            line.append(get_digest(file_path))
            line.append(os.path.getsize(file_path))
            manifest.append(",".join(str(item) for item in line))
    return manifest


def traverse_s3(s3_path, exclude=None):
    """
    Traverse a given S3 bucket path and generate the PULP_MANIFEST
    associated with it.

    :param s3_path: str
    :param exclude: str, optional glob pattern to exclude files or directories
    :return: list of pulp manifest items
    """
    try:
        import boto3
    except ImportError:
        print("Error: The 'boto3' package is required for S3 support. Please install it with 'pip install pulp-manifest[s3]'.")
        sys.exit(1)
    manifest = []
    parsed_url = urlparse(s3_path)
    bucket_name = parsed_url.netloc
    prefix = parsed_url.path.lstrip("/")

    s3_client = boto3.client("s3")
    paginator = s3_client.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        if "Contents" in page:
            for obj in page["Contents"]:
                key = obj["Key"]
                if exclude and fnmatch.fnmatch(key, f"*{exclude}*"):
                    continue
                if key == "PULP_MANIFEST":
                    continue
                line = []
                line.append(key.removeprefix(prefix).lstrip('/')) # Remove the prefix from the key
                response = s3_client.get_object(Bucket=bucket_name, Key=key)
                file_content = response["Body"].read()
                digest = sha256(file_content).hexdigest()
                line.append(digest)
                line.append(str(obj["Size"]))
                manifest.append(",".join(str(item) for item in line))

    return manifest


def main():
    """
    Main
    """
    parser = argparse.ArgumentParser(
        description="Generate a PULP_MANIFEST file for a given directory or S3 bucket path."
    )
    parser.add_argument(
        "directory",
        help="A path to the directory where the PULP_MANIFEST"
        " file should be created.",
    )
    parser.add_argument(
        "-e", "--exclude",
        metavar="PATTERN",
        help="Exclude files or directories matching the given glob pattern from the PULP_MANIFEST."
    )
    args = parser.parse_args()
    directory = args.directory
    exclude = args.exclude

    # Remove PULP_MANIFEST if it already exists in the given directory
    try:
        os.remove(os.path.join(directory, "PULP_MANIFEST"))
    except (IOError, OSError):
        pass

    try:
        if directory.startswith("s3://"):
            print(f"Generating PULP_MANIFEST for S3 bucket: {directory} with exclude: {exclude}")
            manifest = traverse_s3(directory, exclude)
        else:
            print(f"Generating PULP_MANIFEST for directory: {directory}")
            manifest = traverse_dir(directory, exclude)
        write_manifest("PULP_MANIFEST", manifest)
    except (IOError, OSError) as e:
        print(
            "Couldn't open or write PULP_MANIFEST to directory %s (%s)."
            % (directory, e)
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
    sys.exit(0)
