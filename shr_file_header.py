import struct

# 'H' is for uint16_t, 'I' is for uint32_t, 'Q' is for uint64_t, 'd' is for double, 'f' is for float, and 'h' is for uint16_t[128]
# '128h' is used for uint16_t title[128] and '16I' is used for uint32_t reserved2[16]
shr_header_struct_format = (
    "H"  # uint16_t signature
    "H"  # uint16_t version
    "I"  # uint32_t reserved1
    "Q"  # uint64_t dataOffset
    "I"  # uint32_t sweepCount
    "I"  # uint32_t sweepLength
    "d"  # double firstBinFreqHz
    "d"  # double binSizeHz
    "128H"  # uint16_t title[128]
    "d"  # double centerFreqHz
    "d"  # double spanHz
    "d"  # double rbwHz
    "d"  # double vbwHz
    "f"  # float refLevel
    "I"  # uint32_t refScale
    "f"  # float div
    "I"  # uint32_t window
    "i"  # int32_t attenuation
    "i"  # int32_t gain
    "i"  # int32_t detector
    "i"  # int32_t processingUnits
    "d"  # double windowBandwidth
    "i"  # int32_t decimationType
    "i"  # int32_t decimationDetector
    "i"  # int32_t decimationCount
    "i"  # int32_t decimationTimeMs
    "i"  # int32_t channelizeEnabled
    "i"  # int32_t channelOutputUnits
    "d"  # double channelCenterHz
    "d"  # double channelWidthHz
    "16I"  # uint32_t reserved2[16]
)

# Calculate the size of the struct
shr_header_struct_size = struct.calcsize(shr_header_struct_format)


def read_string_from_bytes(input_bytes: tuple[int,]) -> str:
    removed_zero_bytes = [byte for byte in input_bytes if byte != 0]
    string = bytes(removed_zero_bytes).decode("ascii")
    return string.strip()


def read_shr_header(file) -> dict:  # file from open(...)
    # navigate file
    original_position = file.tell()
    file.seek(0, 0)
    data_bytes = file.read(shr_header_struct_size)
    file.seek(original_position)

    # Convert the unpacked data to a dictionary for easier access and readability
    unpacked_data = struct.unpack(shr_header_struct_format, data_bytes)
    data_dict = {
        "signature": unpacked_data[0],
        "version": unpacked_data[1],
        "reserved1": unpacked_data[2],
        "dataOffset": unpacked_data[3],
        "sweepCount": unpacked_data[4],
        "sweepLength": unpacked_data[5],
        "firstBinFreqHz": unpacked_data[6],
        "binSizeHz": unpacked_data[7],
        "title": read_string_from_bytes(unpacked_data[8:136]),
        "centerFreqHz": unpacked_data[136],
        "spanHz": unpacked_data[137],
        "rbwHz": unpacked_data[138],
        "vbwHz": unpacked_data[139],
        "refLevel": unpacked_data[140],
        "refScale": unpacked_data[141],
        "div": unpacked_data[142],
        "window": unpacked_data[143],
        "attenuation": unpacked_data[144],
        "gain": unpacked_data[145],
        "detector": unpacked_data[146],
        "processingUnits": unpacked_data[147],
        "windowBandwidth": unpacked_data[148],
        "decimationType": unpacked_data[149],
        "decimationDetector": unpacked_data[150],
        "decimationCount": unpacked_data[151],
        "decimationTimeMs": unpacked_data[152],
        "channelizeEnabled": unpacked_data[153],
        "channelOutputUnits": unpacked_data[154],
        "channelCenterHz": unpacked_data[155],
        "channelWidthHz": unpacked_data[156],
        "reserved2": read_string_from_bytes(unpacked_data[157:173]),
    }

    return data_dict
