import struct

# Define the format string for the SHRSweepHeader struct
shr_sweep_header_struct_format = (
    "Q"  # uint64_t timestamp - milliseconds since epoch
    "d"  # double latitude
    "d"  # double longitude
    "d"  # double altitude - meters
    "B"  # uint8_t adcOverflow
    "15s"  # uint8_t reserved[15]
)

# Calculate the size of the struct
shr_sweep_header_struct_size = struct.calcsize(shr_sweep_header_struct_format)


def read_shr_sweep_headers(file, shr_header: dict) -> list[dict]:
    original_position = file.tell()

    float_size = struct.calcsize("f")
    file.seek(shr_header["dataOffset"], 0)
    sweep_headers = []
    for i in range(shr_header["sweepCount"]):
        # Convert the unpacked data to a dictionary for easier access and readability
        data_bytes = file.read(shr_sweep_header_struct_size)
        unpacked_data = struct.unpack(shr_sweep_header_struct_format, data_bytes)
        data_dict = {
            "timestamp": unpacked_data[0],
            "latitude": unpacked_data[1],
            "longitude": unpacked_data[2],
            "altitude": unpacked_data[3],
            "adcOverflow": unpacked_data[4],
            "reserved": unpacked_data[5],
        }
        sweep_headers.append(data_dict)
        # navigate file
        file.seek(shr_header["sweepLength"] * float_size, 1)  # skip sweep data

    file.seek(original_position, 0)

    return sweep_headers
