# Copyright 2024-2025 XMOS LIMITED.
# This Software is subject to the terms of the XMOS Public Licence: Version 1.
"""Time domain block FIR generator."""

import numpy as np
import argparse
import os
from pathlib import Path
import warnings
from copy import deepcopy

def quantize_array(coefs: np.ndarray, exp: float):
    """
    Quantise an np.ndarray with exponent exp.

    Parameters
    ----------
    coefs : np.ndarray
        Array of floats to be quanntised
    exp : float
        Exponent to use for the quantisation

    Returns
    -------
    np.array
         Array of ints
    """
    quantised = np.rint(np.ldexp(coefs, exp))
    quantised_and_clipped = np.clip(quantised, np.iinfo(np.int32).min, np.iinfo(np.int32).max)
    assert np.allclose(quantised, quantised_and_clipped)
    return np.array(quantised_and_clipped, dtype=np.int64)


def _calc_max_accu(quantised_coefs, vpu_shr=30):
    v = np.where(quantised_coefs > 0, np.iinfo(np.int32).max, np.iinfo(np.int32).min)
    v = np.array(v, dtype=np.int64)
    accu = 0
    for x, y in zip(v, quantised_coefs):
        accu += np.int64(np.rint((x * y) / 2**vpu_shr))
    return accu


def _emit_filter(fh, coefs_padded, name, block_length, bits_per_element=32):
    vpu_shr = 30  # the CPU shifts the product before accumulation
    vpu_accu_bits = 40

    # reverse the filter
    coefs_padded = coefs_padded[::-1]

    coef_data_name = "coefs_" + name

    max_val = np.max(np.abs(coefs_padded))
    _, e = np.frexp(max_val)
    exp = bits_per_element - 2 - e

    quantised_coefs = quantize_array(coefs_padded, exp)
    max_accu = _calc_max_accu(quantised_coefs, vpu_shr)

    # This guarentees no accu overflow
    while max_accu > 2 ** (vpu_accu_bits - 1) - 1:
        exp -= 1
        quantised_coefs = quantize_array(coefs_padded, exp)
        max_accu = _calc_max_accu(quantised_coefs)

    if exp != vpu_shr:
        if exp < vpu_shr:
            f = vpu_shr - exp
            print("Warning: safe input limits is now restricted to [int_max/%d, int_min/%d]"%(2**f, 2**f))
        exp = vpu_shr
        quantised_coefs = quantize_array(coefs_padded, exp)
        max_accu = _calc_max_accu(quantised_coefs)

    fh.write(
        "int32_t __attribute__((aligned (8))) "
        + coef_data_name
        + "["
        + str(len(coefs_padded))
        + "] = {\n"
    )
    counter = 1
    for val in quantised_coefs:
        fh.write("%12d" % (val))
        if counter != len(coefs_padded):
            fh.write(",\t")
        if counter % 4 == 0:
            fh.write("\n")
        counter += 1
    fh.write("};\n")

    return quantised_coefs


def generate_td_fir(
    td_coefs: np.ndarray,
    filter_name: str,
    output_path: Path,
    frame_advance=8,
    gain_dB=0.0,
    verbose=False,
):
    """
    Convert the input filter coefficients array into a header with block
    time domain structures to be included in a C project.

    Parameters
    ----------
    td_coefs : np.ndarray
        This is a 1D numpy float array of the coefficients of the filter.
    filter_name : str
        For use in identification of the filter from within the C code.
        All structs and defines that pertain to this filter will contain
        this identifier.
    output_path : str
        Where to output the resulting header file.
    frame_advance : int, optional
        The size in samples of a frame, measured in time domain samples,
        by default 8. Only multiples of 8 are supported.
    gain_dB : float, optional
        A gain applied to the filter's output, by default 0.0
    verbose : bool, optional
        Enable verbose printing, by default False

    Raises
    ------
        ValueError: Bad config - Must be fixed
    """
    output_file_name = os.path.join(output_path, filter_name + ".h")

    original_filter_length = len(td_coefs)

    if frame_advance != 8:
        raise ValueError("Bad config: Only frame_advance of 8 currently supported.")

    if frame_advance > 64:
        warnings.warn(
            "For frame_advance > 64, a frequency domain implementation is likely more"
            "efficient, please see AN02027, and try generate_fd_fir instead.",
            UserWarning,
        )

    # this is the above but rounded up to the nearest block_length
    target_filter_bank_length = (
        (original_filter_length + frame_advance - 1) // frame_advance
    ) * frame_advance

    if original_filter_length != target_filter_bank_length:
        warnings.warn(f"{filter_name} will be zero padded to length {target_filter_bank_length}")
        padding = np.zeros(target_filter_bank_length - original_filter_length)
        prepared_coefs = np.concatenate((td_coefs, padding))
    else:
        prepared_coefs = td_coefs

    # Apply the gains
    prepared_coefs = prepared_coefs * 10.0 ** (gain_dB / 20.0)

    with open(output_file_name, "w") as fh:
        fh.write('#include "td_block_fir.h"\n\n')

        # The count of blocks in the filter ( the data is at least 2 more)
        filter_block_count = target_filter_bank_length // frame_advance

        quantized_coefs = _emit_filter(
            fh, prepared_coefs, filter_name, frame_advance
        )

        # emit the data define
        data_block_count = filter_block_count + 2
        fh.write("//This is the count of int32_t words to allocate for one data channel.\n")
        fh.write(
            "//i.e. int32_t channel_data[" + filter_name + "_DATA_BUFFER_ELEMENTS] = { 0 };\n"
        )
        fh.write(
            "#define "
            + filter_name
            + "_DATA_BUFFER_ELEMENTS ("
            + str(data_block_count * frame_advance)
            + ")\n\n"
        )

        fh.write("#define " + filter_name + "_TD_BLOCK_LENGTH (" + str(frame_advance) + ")\n")
        fh.write("#define " + filter_name + "_BLOCK_COUNT (" + str(filter_block_count) + ")\n")
        fh.write("#define " + filter_name + "_FRAME_ADVANCE (" + str(frame_advance) + ")\n")
        fh.write("#define " + filter_name + "_FRAME_OVERLAP (" + str(0) + ")\n")

    return prepared_coefs, quantized_coefs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optional app description")

    parser.add_argument("filter", type=str, help="path to the filter(numpy format)")
    parser.add_argument("--gain", type=float, default=0.0, help="Apply a gain to the output(dB).")
    parser.add_argument("--output", type=str, default=".", help="Output location.")
    parser.add_argument(
        "--name",
        type=str,
        default=None,
        help="Name for the filter(override the default which is the filename)",
    )

    args = parser.parse_args()

    output_path = os.path.realpath(args.output)
    filter_path = os.path.realpath(args.filter)
    gain_dB = args.gain

    if os.path.exists(filter_path):
        coefs = np.load(filter_path)
    else:
        raise FileNotFoundError(f"Error: cannot find {filter_path}")
        exit(1)

    if args.name != None:
        filter_name = args.name
    else:
        p = os.path.basename(filter_path)
        filter_name = p.split(".")[0]

    os.makedirs(args.output, exist_ok=True)

    generate_td_fir(coefs, filter_name, output_path, gain_dB=gain_dB)
