"""
StegoCrypt Steganography Module (Ultra-Lite)
--------------------------------------------
Optimized for Low-RAM environments (Streamlit Cloud).
Modifies pixels IN-PLACE instead of creating new lists.

Author: Turkay Yildirim
License: MIT
"""

from PIL import Image
from io import BytesIO
from typing import Union, Generator

def bin_to_bytes(binary_data):
    all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8)]
    return bytearray([int(byte, 2) for byte in all_bytes])

def bit_generator(data: bytes) -> Generator[int, None, None]:
    for byte in data:
        for i in range(7, -1, -1):
            yield (byte >> i) & 1

def encode_image(image_source: Union[str, BytesIO], secret_data: bytes, output_dest: Union[str, BytesIO], progress_callback=None):
    if hasattr(image_source, 'seek'):
        image_source.seek(0)

    img = Image.open(image_source)
    img = img.convert("RGB")

    pixels = img.load()
    width, height = img.size
    total_pixels = width * height

    data_len = len(secret_data)
    total_payload_bits = 32 + (data_len * 8)

    if total_payload_bits > total_pixels * 3:
        raise ValueError(f"Image too small! Need {total_payload_bits/8/1024:.1f} KB capacity.")

    header_bits = ((data_len >> i) & 1 for i in range(31, -1, -1))

    def full_payload():
        yield from header_bits
        yield from bit_generator(secret_data)

    payload = full_payload()

    idx = 0
    try:
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]

                try:
                    bit = next(payload)
                    r = (r & 0xFE) | bit
                    idx += 1
                except StopIteration:
                    pixels[x, y] = (r, g, b)
                    raise

                try:
                    bit = next(payload)
                    g = (g & 0xFE) | bit
                    idx += 1
                except StopIteration:
                    pixels[x, y] = (r, g, b)
                    raise

                try:
                    bit = next(payload)
                    b = (b & 0xFE) | bit
                    idx += 1
                except StopIteration:
                    pixels[x, y] = (r, g, b)
                    raise

                pixels[x, y] = (r, g, b)

                if progress_callback and idx % 150000 == 0:
                    progress_callback(min(idx / total_payload_bits, 1.0))

    except RuntimeError:
        pass
    except StopIteration:
        pass

    if progress_callback: progress_callback(0.99)
    img.save(output_dest, format="PNG")
    if progress_callback: progress_callback(1.0)
    return True

def decode_image(image_source: Union[str, BytesIO], progress_callback=None):
    if hasattr(image_source, 'seek'):
        image_source.seek(0)

    img = Image.open(image_source)
    img = img.convert("RGB")
    pixels = img.load()
    width, height = img.size

    header_bits = []
    count = 0

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            for val in (r, g, b):
                header_bits.append(str(val & 1))
                count += 1
                if count >= 32: break
            if count >= 32: break
        if count >= 32: break

    data_len = int("".join(header_bits), 2)
    total_bits_needed = data_len * 8

    binary_list = []
    bits_read = 0

    try:
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                for val in (r, g, b):
                    binary_list.append(str(val & 1))
                    bits_read += 1
                    if bits_read >= 32 + total_bits_needed:
                        raise StopIteration

                if progress_callback and bits_read % 150000 == 0:
                    progress_callback(bits_read / (32 + total_bits_needed))
    except StopIteration:
        pass

    full_str = "".join(binary_list)
    extracted_bin = full_str[32 : 32 + total_bits_needed]

    return bin_to_bytes(extracted_bin)