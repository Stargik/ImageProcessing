"""Manual image processing functions using PixelAccess and nested loops."""

import math
from PIL import Image


def _clamp(value):
    """Clamp numeric value to valid 8-bit channel range."""
    value = int(round(value))
    if value < 0:
        return 0
    if value > 255:
        return 255
    return value


def _to_rgb(pixel):
    """Normalize a source pixel into an RGB tuple."""
    if isinstance(pixel, int):
        return pixel, pixel, pixel
    if len(pixel) >= 3:
        return pixel[0], pixel[1], pixel[2]
    if len(pixel) == 2:
        return pixel[0], pixel[0], pixel[0]
    return 0, 0, 0


def apply_grayscale(image):
    width, height = image.size
    result = Image.new("RGB", (width, height))

    src_pixels = image.load()
    dst_pixels = result.load()

    for y in range(height):
        for x in range(width):
            red, green, blue = _to_rgb(src_pixels[x, y])
            gray = _clamp(0.299 * red + 0.587 * green + 0.114 * blue)
            dst_pixels[x, y] = (gray, gray, gray)

    return result


def apply_brightness(image, value):
    width, height = image.size
    result = Image.new("RGB", (width, height))

    src_pixels = image.load()
    dst_pixels = result.load()

    for y in range(height):
        for x in range(width):
            red, green, blue = _to_rgb(src_pixels[x, y])
            dst_pixels[x, y] = (
                _clamp(red + value),
                _clamp(green + value),
                _clamp(blue + value),
            )

    return result


def apply_box_filter(image, kernel_size):
    if kernel_size < 3 or kernel_size % 2 == 0:
        raise ValueError("kernel_size must be odd and >= 3")

    width, height = image.size
    result = Image.new("RGB", (width, height))

    src_pixels = image.load()
    dst_pixels = result.load()

    offset = kernel_size // 2
    area = kernel_size * kernel_size

    for y in range(height):
        for x in range(width):
            if x < offset or x >= width - offset or y < offset or y >= height - offset:
                dst_pixels[x, y] = _to_rgb(src_pixels[x, y])
                continue

            sum_red = 0
            sum_green = 0
            sum_blue = 0

            for ky in range(-offset, offset + 1):
                for kx in range(-offset, offset + 1):
                    px, py = x + kx, y + ky
                    red, green, blue = _to_rgb(src_pixels[px, py])
                    sum_red += red
                    sum_green += green
                    sum_blue += blue

            dst_pixels[x, y] = (
                _clamp(sum_red / area),
                _clamp(sum_green / area),
                _clamp(sum_blue / area),
            )

    return result


def apply_sobel(image):
    grayscale = apply_grayscale(image)
    width, height = grayscale.size
    result = Image.new("RGB", (width, height))

    src_pixels = grayscale.load()
    dst_pixels = result.load()

    gx_kernel = (
        (-1, 0, 1),
        (-2, 0, 2),
        (-1, 0, 1),
    )
    gy_kernel = (
        (-1, -2, -1),
        (0, 0, 0),
        (1, 2, 1),
    )

    for y in range(height):
        for x in range(width):
            if x == 0 or y == 0 or x == width - 1 or y == height - 1:
                dst_pixels[x, y] = src_pixels[x, y]
                continue

            grad_x = 0
            grad_y = 0

            for ky in range(-1, 2):
                for kx in range(-1, 2):
                    pixel_value = src_pixels[x + kx, y + ky][0]
                    grad_x += pixel_value * gx_kernel[ky + 1][kx + 1]
                    grad_y += pixel_value * gy_kernel[ky + 1][kx + 1]

            magnitude = _clamp(math.sqrt(grad_x * grad_x + grad_y * grad_y))
            dst_pixels[x, y] = (magnitude, magnitude, magnitude)

    return result


def apply_threshold(image, threshold):
    grayscale = apply_grayscale(image)
    width, height = grayscale.size
    result = Image.new("RGB", (width, height))

    src_pixels = grayscale.load()
    dst_pixels = result.load()
    threshold = _clamp(threshold)

    for y in range(height):
        for x in range(width):
            value = src_pixels[x, y][0]
            if value >= threshold:
                dst_pixels[x, y] = (255, 255, 255)
            else:
                dst_pixels[x, y] = (0, 0, 0)

    return result
