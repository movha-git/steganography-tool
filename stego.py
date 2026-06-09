from PIL import Image

def encode_message(image_path, message, output_path):
    """Hide a secret message inside an image using LSB steganography"""
    
    img = Image.open(image_path).convert('RGB')
    pixels = list(img.getdata())

    # Add delimiter so decoder knows where message ends
    message += '<<<END>>>'

    # Convert message to binary
    binary_message = ''.join(format(ord(c), '08b') for c in message)

    # Check if image is large enough to hold the message
    if len(binary_message) > len(pixels) * 3:
        raise ValueError(
            f'Message too long! Max characters for this image: {(len(pixels) * 3) // 8 - 9}'
        )

    new_pixels = []
    bit_index  = 0

    for pixel in pixels:
        r, g, b = pixel

        # Replace least significant bit of each channel with message bit
        if bit_index < len(binary_message):
            r = (r & ~1) | int(binary_message[bit_index])
            bit_index += 1

        if bit_index < len(binary_message):
            g = (g & ~1) | int(binary_message[bit_index])
            bit_index += 1

        if bit_index < len(binary_message):
            b = (b & ~1) | int(binary_message[bit_index])
            bit_index += 1

        new_pixels.append((r, g, b))

    # Save new image with hidden message
    new_img = Image.new('RGB', img.size)
    new_img.putdata(new_pixels)
    new_img.save(output_path, 'PNG')

    return f'Message successfully hidden! Saved as {output_path}'


def decode_message(image_path):
    """Extract a hidden message from an image"""
    
    img    = Image.open(image_path).convert('RGB')
    pixels = list(img.getdata())

    # Extract least significant bit from each channel
    bits = ''
    for pixel in pixels:
        for channel in pixel:
            bits += str(channel & 1)

    # Convert bits back to characters
    chars   = [bits[i:i+8] for i in range(0, len(bits), 8)]
    message = ''

    for char in chars:
        letter = chr(int(char, 2))
        message += letter
        # Stop when we find the delimiter
        if message.endswith('<<<END>>>'):
            return message[:-9]

    return 'No hidden message found in this image.'