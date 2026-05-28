import os
import sys
import zipfile


if __name__ != "__main__":
    sys.exit(1)

assert len(sys.argv) in [5, 6], "Usage: archive.py -Path <staging_root> -DestinationPath <destination_path> -Force"
assert sys.argv[1] == "-Path", "Expected -Path argument"
assert sys.argv[3] == "-DestinationPath", "Expected -DestinationPath argument"
if len(sys.argv) == 6 and sys.argv[5] != "-Force":
    assert False, "Expected -Force argument"
orig = sys.argv[2]
dest = sys.argv[4]
assert os.path.exists(orig), f"Source path '{orig}' does not exist"
assert os.path.isdir(orig), f"Source path '{orig}' is not a directory"
if os.path.exists(dest) and os.path.isdir(dest):
    assert False, f"Destination path '{dest}' is a folder."
if os.path.exists(dest) and len(sys.argv) != 6:
    assert False, f"Destination path '{dest}' already exists. Use -Force to overwrite."
if os.path.exists(dest):
    os.remove(dest)


with zipfile.ZipFile(dest, "w") as zf:
    for root, _, files in os.walk(orig):
        for file in files:
            path = os.path.join(root, file)
            zf.write(path, os.path.relpath(path, orig))
