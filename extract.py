path_oli = r"PATH_TO_YOUR_OLI_FILES"

import struct
import argparse

parser = argparse.ArgumentParser(
                    prog='OliExtractor',
                    description='Extracts content from oli files (Zombi(U))',
                    epilog='This script has not been tested on other games.')

parser.add_argument('-f', '--force', action='store_true')
args = parser.parse_args()

def read_utf16le_string(data, offset, override_next_offset: int = None):
    next_offset = 0xE if not override_next_offset else override_next_offset

    # Read the length (2 bytes, little endian)
    length_bytes = data[offset:offset+2]
    (length,) = struct.unpack('<H', length_bytes)

    # Calculate the actual byte size of the string (UTF-16LE = 2 bytes per character)
    string_bytes = data[offset+2 : offset+2+length]
    
    # Decode using UTF-16LE
    text = string_bytes.decode('utf-16le')
    return text, offset + 2 + length + next_offset

def extract_file(file):
    texts = []
    with open(file, "rb") as f:
        data = f.read()
    try:

        filename, next_offset = read_utf16le_string(data, offset=0x2d, override_next_offset=0x4)
        texts.append(filename)

        if data[next_offset-1:next_offset] == b'\x01': # LYN_OUTPUT file
            lyn, next_offset = read_utf16le_string(data, offset=next_offset, override_next_offset=0x2)
            agent, next_offset = read_utf16le_string(data, offset=next_offset, override_next_offset=0x2)

        while next_offset < len(data)-1:
            # Then read the next block (e.g., first translation string)
            text1, next_offset = read_utf16le_string(data, offset=next_offset)
            texts.append(text1)
    except UnicodeDecodeError as e:
        if args.force:
            return texts
        else:
            raise e

from pathlib import Path

oli_dir = Path(path_oli)
oli_files = oli_dir.glob("*.oli")
broken_files = []

with open("olis.csv", 'w', encoding="utf-8") as f:
    for file in oli_files:
        try:
            content = extract_file(file.as_posix())
            if content == None:
                continue
            line = ",".join(content).replace("\u0000", "")

            f.write(line+"\n")
        except UnicodeDecodeError as e:
            broken_files.append(file)

if len(broken_files) > 0:
    print("Some files were not extracted. You can find a detailed list in not_extracted.txt")
    print("You can relaunch the script with the -f option to write what can be extracted from the files")
    print("Corruption might only be at the end of the file, allowing you to extract all usable data from the file.")
    with open("not_extracted.txt", "w", encoding="utf-8") as errFile:
        for line in map(lambda x: x.as_posix() + "\n", broken_files):
            errFile.write(line)
