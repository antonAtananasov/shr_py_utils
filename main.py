from shr_convert import *

# USER SETTINGS
DEFAULT_TARGET_DIR: str = "./test"
CONVERSION_FORMAT: str = "fits"  # from CONVERSION_FORMATS
COMPRESS_FITS: bool = True


CONVERSION_FORMATS: dict[str, callable] = {"fits": shr_to_fits, "csv": shr_to_csv}
RECURSIVE: bool = True


def main():
    target_dir = os.path.relpath(
        input(f"Target directory [{DEFAULT_TARGET_DIR}]: ") or DEFAULT_TARGET_DIR
    )
    format = (
        input(
            f"Conversion format [{'/'.join([(fmt.upper() if fmt==CONVERSION_FORMAT else fmt) for fmt in CONVERSION_FORMATS.keys()])}]: "
        )
        or CONVERSION_FORMAT
    )
    if not format in CONVERSION_FORMATS.keys():
        print("No such conversion format available")
        return
    if format == "fits":
        compress = (
            input(f"Compress fits data [{'Y/n' if COMPRESS_FITS else 'y/N'}]: ").lower()
            == "y"
        )
        convert_directory(target_dir, CONVERSION_FORMATS[format], compress)
    else:
        convert_directory(target_dir, CONVERSION_FORMATS[format])


if __name__ == "__main__":
    main()
