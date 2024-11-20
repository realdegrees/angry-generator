from PIL import Image, ImageDraw, ImageFont
from util import process_caption, load_font

def create_image(caption, image_path):
    
    def split_text_into_lines(caption, canvas, font, max_width):
        words = caption.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = f'{current_line} {word}'.strip()
            bbox = canvas.textbbox((0, 0), test_line, font=font, spacing=0, stroke_width=4)
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
    font = ImageFont.truetype(load_font(caption))
    max_width = image.width * 0.9
    lines = split_text_into_lines(caption, canvas, font, max_width)
    draw_text_on_image(canvas, lines, font, image)

    return image
