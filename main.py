from datetime import datetime
import re
import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from matplotlib.ticker import MaxNLocator
from matplotlib.colors import LogNorm
from shr_file_header import read_shr_header
from shr_sweep_header import read_shr_sweep_headers
from shr_sweep_data import read_shr_sweeps


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

        data = np.array(shr_sweeps)
        # Create a PrimaryHDU object
        hdu = fits.PrimaryHDU(data if not compress else None)
        comp_hdu = fits.CompImageHDU(data if compress else None)

        # load header
        header = hdu.header
        header["COMMENT"] = f"This file was converted to FITS from {file_name}"
        header["DATE"] = datetime.now().strftime("%Y-%m-%d")
        for k, v in shr_header.items():
            key = re.sub(r"(?<!^)(?=[A-Z])", "_", k).upper()
            tag = f"HIERARCH {key}"
            header[tag] = v

            # Create an HDUList to contain the HDU
        hdul = fits.HDUList([hdu, comp_hdu] if compress else [hdu])

        file_prefix = file_name.split(".")[0]
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


def main():
    shr_to_fits("example.shr")
    fits_plot("example.fits")


if __name__ == "__main__":
    main()
