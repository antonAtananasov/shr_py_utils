import struct
from shr_sweep_header import shr_sweep_header_struct_size


def read_shr_sweeps(file, shr_header: dict) -> list[tuple[float]]:
    original_position = file.tell()
    float_size = struct.calcsize("f")
    file.seek(shr_header["dataOffset"], 0)
    sweeps = []
    for i in range(shr_header["sweepCount"]):
        # navigate file
        file.seek(shr_sweep_header_struct_size, 1)  # skip sweep header
        # Convert the unpacked data to a dictionary for easier access and readability
        data_bytes = file.read(shr_header["sweepLength"] * float_size)
        unpacked_data = struct.unpack(f"{shr_header['sweepLength']}f", data_bytes)
        sweeps.append(unpacked_data)

    file.seek(original_position, 0)

    return sweeps
