from PIL import Image
from io import BytesIO
from typing import Union

def data_to_bin(data):
    if isinstance(data, str):
        return ''.join([format(ord(i), "08b") for i in data])
    elif isinstance(data, bytes):
        return ''.join([format(i, "08b") for i in data])
    elif isinstance(data, int):
        return format(data, "08b")
    else:
        raise TypeError("Unsupported data type.")

def bin_to_bytes(binary_data):
    all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8)]
    return bytearray([int(byte, 2) for byte in all_bytes])

def encode_image(image_source: Union[str, BytesIO], secret_data, output_dest: Union[str, BytesIO], progress_callback=None):
    if hasattr(image_source, 'seek'):
        image_source.seek(0)

    img = Image.open(image_source)
    img = img.convert("RGB")

    data_len = len(secret_data)
    bin_length = format(data_len, '032b')
    bin_data = data_to_bin(secret_data)
    full_payload = bin_length + bin_data
    payload_len = len(full_payload)

    width, height = img.size
    total_pixels = width * height

    if payload_len > total_pixels * 3:
        raise ValueError("Error: Image is too small to hold this data.")

    pixels = list(img.getdata())
    encoded_pixels = []

    payload_index = 0

    for i, (r, g, b) in enumerate(pixels):
        if payload_index >= payload_len:
            encoded_pixels.extend(pixels[i:])
            break

        if payload_index < payload_len:
            r = (r & 0xFE) | int(full_payload[payload_index])
            payload_index += 1

        if payload_index < payload_len:
            g = (g & 0xFE) | int(full_payload[payload_index])
            payload_index += 1

        if payload_index < payload_len:
            b = (b & 0xFE) | int(full_payload[payload_index])
            payload_index += 1

        encoded_pixels.append((r, g, b))

        if progress_callback and i % 50000 == 0:
            current_percent = payload_index / payload_len
            progress_callback(current_percent)

    if progress_callback:
        progress_callback(0.99)

    new_img = Image.new(img.mode, img.size)
    new_img.putdata(encoded_pixels)

    new_img.save(output_dest, format="PNG")

    if progress_callback:
        progress_callback(1.0)
    return True

def decode_image(image_source: Union[str, BytesIO], progress_callback=None):
    if hasattr(image_source, 'seek'):
        image_source.seek(0)

    img = Image.open(image_source)
    img = img.convert("RGB")
    pixels = list(img.getdata())

    header_pixels = pixels[:12]

    header_bin_list = []
    for r, g, b in header_pixels:
        header_bin_list.append(str(r & 1))
        header_bin_list.append(str(g & 1))
        header_bin_list.append(str(b & 1))

    header_bin_str = "".join(header_bin_list)[:32]
    data_len = int(header_bin_str, 2)

    total_bits_needed = 32 + (data_len * 8)
    total_pixels_needed = (total_bits_needed + 2) // 3

    if total_pixels_needed > len(pixels):
        return b""

    pixels_to_read = pixels[:total_pixels_needed]

    binary_list = []
    total_count = len(pixels_to_read)

    for i, (r, g, b) in enumerate(pixels_to_read):
        binary_list.append(str(r & 1))
        binary_list.append(str(g & 1))
        binary_list.append(str(b & 1))

        if progress_callback and i % 50000 == 0:
            progress_callback(i / total_count)

    full_binary_str = "".join(binary_list)
    extracted_bin = full_binary_str[32 : 32 + (data_len * 8)]

    if progress_callback:
        progress_callback(1.0)

    return bin_to_bytes(extracted_bin)
