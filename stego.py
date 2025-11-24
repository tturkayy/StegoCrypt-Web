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
    data_len = len(secret_data)
    header_bits = [(data_len >> i) & 1 for i in range(31, -1, -1)]
    def full_payload_generator():
        yield from header_bits
        yield from bit_generator(secret_data)
    payload_iter = full_payload_generator()
    total_payload_bits = 32 + (data_len * 8)
    width, height = img.size
    total_pixels = width * height
    if total_payload_bits > total_pixels * 3:
        raise ValueError("Error: Image is too small to hold this data.")
    pixels = list(img.getdata())
    encoded_pixels = []
    bits_processed = 0
    data_exhausted = False
    for i, (r, g, b) in enumerate(pixels):
        if data_exhausted:
            encoded_pixels.extend(pixels[i:])
            break
        try:
            bit = next(payload_iter)
            r = (r & 0xFE) | bit
            bits_processed += 1
        except StopIteration:
            data_exhausted = True
        if not data_exhausted:
            try:
                bit = next(payload_iter)
                g = (g & 0xFE) | bit
                bits_processed += 1
            except StopIteration:
                data_exhausted = True
        if not data_exhausted:
            try:
                bit = next(payload_iter)
                b = (b & 0xFE) | bit
                bits_processed += 1
            except StopIteration:
                data_exhausted = True
        encoded_pixels.append((r, g, b))
        if progress_callback and i % 50000 == 0:
            progress_callback(min(bits_processed / total_payload_bits, 1.0))
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
    header_bits = []
    pixel_iter = iter(pixels)
    bits_read = 0
    while bits_read < 32:
        try:
            r, g, b = next(pixel_iter)
            header_bits.append(str(r & 1))
            if len(header_bits) < 32: header_bits.append(str(g & 1))
            if len(header_bits) < 32: header_bits.append(str(b & 1))
            bits_read = len(header_bits)
        except StopIteration:
            break
    header_bin_str = "".join(header_bits)
    data_len = int(header_bin_str, 2)
    total_bits_needed = data_len * 8
    total_pixels_needed = (32 + total_bits_needed + 2) // 3
    if total_pixels_needed > len(pixels):
        return b""
    pixels_to_read = pixels[:total_pixels_needed]
    binary_list = []
    for r, g, b in pixels_to_read:
        binary_list.append(str(r & 1))
        binary_list.append(str(g & 1))
        binary_list.append(str(b & 1))
    full_binary_str = "".join(binary_list)
    extracted_bin = full_binary_str[32 : 32 + total_bits_needed]
    return bin_to_bytes(extracted_bin)
