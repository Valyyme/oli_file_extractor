import struct

def read_title(data):
    offset = 0x2d
    length_bytes = data[offset:offset+2]
    (length,) = struct.unpack('<H', length_bytes)

    string_bytes = data[offset+2 : offset+2+length]
    text = string_bytes.decode('utf-16le')

    return text, offset + 2 + length + 0x4

def read_utf16le_string(data, offset):
    # Read the length (2 bytes, little endian)
    length_bytes = data[offset:offset+2]
    (length,) = struct.unpack('<H', length_bytes)

    # Calculate the actual byte size of the string (UTF-16LE = 2 bytes per character)
    string_bytes = data[offset+2 : offset+2+length]
    
    # Decode using UTF-16LE
    text = string_bytes.decode('utf-16le')
    return text, offset + 2 + length + 0xE

def extract_file(file):
    texts = []
    with open(file, "rb") as f:
        data = f.read()
    
    filename, next_offset = read_title(data)
    next_offset += (-0xE + 0x4)
    texts.append(filename)

    while next_offset < len(data)-1:
        # Then read the next block (e.g., first translation string)
        text1, next_offset = read_utf16le_string(data, offset=next_offset)
        texts.append(text1)
        

    return texts

from pathlib import Path

oli_dir = Path(r"PATH_TO_YOUR_OLI_FILES")
oli_files = oli_dir.glob("*.oli")

with open("olis.csv", 'w', encoding="utf-8") as f:
    for file in oli_files:
        try:
            content = extract_file(file.as_posix())
            line = ",".join(content).replace("\u0000", "")

            f.write(line+"\n")
        except UnicodeDecodeError as e:
            print(file)
            print(e.reason, e.args)