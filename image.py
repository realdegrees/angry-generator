from PIL import Image, ImageDraw, ImageFont
from flask import request
import os


def calculate_font_size(caption, base_font_size=170):
    # Adjust the font size based on the length of the caption
    max_length = 20  # Maximum length for the base font size
    if len(caption) > max_length:
        # Ensure font size doesn't go below 20
        return max(base_font_size - (len(caption) - max_length) * 5, 110)
    return base_font_size

def create_image(caption, image_path):
    def process_caption(caption):
        caption = caption.capitalize()
        if caption.lower().endswith('.gif'):
            caption = caption[:-4]
        return caption

    def load_font():
        font_name = request.args.get('font', 'impact')
        base_font_size = int(request.args.get('font_size', '170'))
        font_size = calculate_font_size(caption, base_font_size)
        font_path = os.path.join('fonts', f'{font_name}.ttf')
        try:
            return ImageFont.truetype(font_path, font_size)
        except OSError:
            return ImageFont.load_default(font_size)

    def split_text_into_lines(caption, draw, font, max_width):
        words = caption.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = f'{current_line} {word}'.strip()
            bbox = draw.textbbox((0, 0), test_line, font=font, spacing=0, stroke_width=4)
            text_width = bbox[2] - bbox[0]
            if text_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def draw_text_on_image(canvas, lines, font, image):
        y = 20
        for line in lines:
            bbox = canvas.textbbox((0, 0), line, font=font, stroke_width=4)
            text_width = bbox[2] - bbox[0]
            x = (image.width - text_width) / 2
            canvas.text((x, y), line, font=font, fill=(255, 255, 255, 255),
                      stroke_width=5, stroke_fill=(0, 0, 0, 255))
            y += bbox[3] - bbox[1] + 10  # Move to the next line with some spacing

    image = Image.open(image_path)
    canvas = ImageDraw.Draw(image)
    caption = process_caption(caption)
    font = load_font()
    max_width = image.width * 0.9
    lines = split_text_into_lines(caption, canvas, font, max_width)
    draw_text_on_image(canvas, lines, font, image)

    return image
