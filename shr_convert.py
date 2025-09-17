from datetime import datetime
import re
import os
import numpy as np
from scipy import stats
from astropy.io import fits
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib.ticker import MaxNLocator
from matplotlib.colors import LogNorm
from shr_file_header import read_shr_header
from shr_sweep_header import read_shr_sweep_headers
from shr_sweep_data import read_shr_sweeps
import csv
from tqdm import tqdm

def shr_plot(file_name: str):
    with open(file_name, "rb") as file:
        # read file
        shr_header = read_shr_header(file)
        shr_sweep_headers = read_shr_sweep_headers(file, shr_header)
        shr_sweeps = read_shr_sweeps(file, shr_header)

        # init graph
        fig, ax = plt.subplots()
        im = ax.imshow(shr_sweeps, interpolation="nearest", aspect="auto")

        # color bar
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel(
            f"Amplitude, {'mV' if shr_header['refScale'] else 'dB'}",
            rotation=-90,
            va="bottom",
        )

        # x axis
        x_tick_labels = (
            np.linspace(
                shr_header["centerFreqHz"] - shr_header["spanHz"] / 2,
                shr_header["centerFreqHz"] + shr_header["spanHz"] / 2,
                shr_header["sweepLength"],
            )
            / 1e6
        )
        ax.set_xticks(np.arange(shr_header["sweepLength"]))
        ax.set_xticklabels(np.round(x_tick_labels, 2))
        ax.xaxis.set_major_locator(MaxNLocator(16))
        plt.xlabel("Freq [MHz]")

        # y axis
        y_tick_labels = [
            datetime.fromtimestamp(header["timestamp"] / 1e3).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            for header in shr_sweep_headers
        ]
        ax.set_yticks(np.arange(shr_header["sweepCount"]))
        ax.set_yticklabels(y_tick_labels)
        ax.yaxis.set_major_locator(MaxNLocator(25))
        plt.ylabel("timestamp")

        ax.set_title(f"Sweep {shr_header['title']} Waterfall".replace("  ", " "))
        plt.show()


def shr_to_fits(file_name: str, compress: bool = True):
    with open(file_name, "rb") as file:
        # read file
        shr_header = read_shr_header(file)
        shr_sweep_headers = read_shr_sweep_headers(file, shr_header)
        shr_sweeps = read_shr_sweeps(file, shr_header)

        if shr_header["sweepLength"] == 0:
            print(f"File {file_name} does not contain sweep data.")
            return

        data = np.array(shr_sweeps)
        # Create a PrimaryHDU object
        hdu = fits.PrimaryHDU(data if not compress else None)
        comp_hdu = fits.CompImageHDU(data if compress else None)

        # load header
        header = hdu.header
        header["COMMENT"] = f"This file was converted to FITS from {file_name}"
        header["NAXIS"] = 2
        header["DATE"] = datetime.now().strftime("%Y-%m-%d")
        timestamps_seconds = np.array([h["timestamp"] for h in shr_sweep_headers]) / 1e3
        start_acuisition_time = datetime.fromtimestamp(timestamps_seconds[0]).strftime(
            "%Y-%m-%dT%H:%M:%S.%f"
        )
        header["DATE-OBS"] = start_acuisition_time
        header["SACQTIME"] = start_acuisition_time
        sweep_bin_durations = timestamps_seconds[1:] - timestamps_seconds[:-1]
        sweep_bin_duration = stats.mode(sweep_bin_durations)[0]  # in s
        end_acuisition_time = datetime.fromtimestamp(
            timestamps_seconds[-1] + sweep_bin_duration  # in s
        ).strftime("%Y-%m-%dT%H:%M:%S.%f")
        header["EACQTIME"] = end_acuisition_time
        header["CTYPE1"] = "time"
        header["CUNIT1"] = "seconds"
        header["CDELT1"] = sweep_bin_duration
        header["CRPIX1"] = 1
        header["CRVAL1"] = start_acuisition_time
        header["CTYPE2"] = "frequency"
        header["CUNIT2"] = "Hz"
        header["CDELT2"] = shr_header["binSizeHz"]
        header["CRPIX2"] = 1
        header["CRVAL2"] = shr_header["firstBinFreqHz"]
        for k, v in shr_header.items():
            key = re.sub(r"(?<!^)(?=[A-Z])", "_", k).upper()
            tag = f"HIERARCH {key}"
            header[tag] = v

            # Create an HDUList to contain the HDU
        hdul = fits.HDUList([hdu, comp_hdu] if compress else [hdu])

        file_prefix = file_name[:file_name.rfind('.')]
        output_filename = f"{file_prefix}.fits"
        hdul.writeto(output_filename, overwrite=True)


def fits_plot(file_name: str):
    with fits.open(file_name) as fits_file:
        image_data = fits_file[1].data

        plt.figure()
        plt.imshow(
            image_data,
            origin="lower",
            aspect="auto",
            interpolation="nearest",
        )
        plt.colorbar()
        plt.show()


def shr_to_csv(file_name: str):
    with open(file_name, "rb") as file:
        shr_header = read_shr_header(file)
        shr_sweep_headers = read_shr_sweep_headers(file, shr_header)
        shr_sweeps = read_shr_sweeps(file, shr_header)

        if shr_header["sweepLength"] == 0:
            print(f"File {file_name} does not contain sweep data.")
            return
        # shr file header
        new_file_name = ".".join(file_name.split(".")[:-1]) + "_header.csv"
        csv_shr_header_keys = shr_header.keys()
        shr_header_data = [shr_header[key] for key in csv_shr_header_keys]
        with open(new_file_name, "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=",")
            csvwriter.writerow(csv_shr_header_keys)
            csvwriter.writerow(shr_header_data)

        # shr sweeps
        new_file_name = ".".join(file_name.split(".")[:-1]) + "_sweep.csv"
        csv_shr_sweep_keys = list(shr_sweep_headers[0].keys())
        csv_shr_sweep_keys = [
            key for key in csv_shr_sweep_keys if not "reserved" in key
        ]
        with open(new_file_name, "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=",")
            csvwriter.writerow(
                ["Sweep Number"]
                + csv_shr_sweep_keys
                + [
                    shr_header["firstBinFreqHz"] + i * shr_header["binSizeHz"]
                    for i in range(len(shr_sweeps[0]))
                ]
            )
            for row in tqdm(
                range(len(shr_sweep_headers)), desc=f"Progress {file_name}"
            ):
                csvwriter.writerow(
                    [row + 1]
                    + [shr_sweep_headers[row][key] for key in csv_shr_sweep_keys]
                    + list(shr_sweeps[row])
                )


def convert_directory(dirpath: str, function: callable, *args):
    # traverse root directory, and list directories as dirs and files as files
    target_files:list[str]=[]
    for root, dirs, files in os.walk(dirpath):
        path = root.split(os.sep)
        # print((len(path) - 1) * '---', os.path.basename(root))
        for file in files:
            # print(len(path) * '---', file)
            full_path = os.path.join(root, file)
            if file.endswith(".shr"):
                target_files.append(full_path)
                
    # add threading here
    for file in target_files:
        try:
            print(f"Processing {file}")
            function(file, *args)
        except Exception as ex:
            print(f"Error processing file {file}: {ex}")
