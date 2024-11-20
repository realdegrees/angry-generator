from PIL import Image, ImageDraw, ImageFont
from util import process_caption, load_font
import textwrap

def create_image(caption, image_path, extension, output): 
    # Open the image    
    image = Image.open(image_path)
    canvas = ImageDraw.Draw(image)
    
    # Process properties
    caption = process_caption(caption)
    font_path, font_size = load_font(caption)
    font = ImageFont.truetype(font_path, font_size)
    max_width = image.width * 0.9
    lines = textwrap.wrap(caption, width=max_width,
                          expand_tabs=False, replace_whitespace=False)
    # Draw Text
    y = 20
    for line in lines:
        bbox = canvas.textbbox((0, 0), line, font=font, stroke_width=4)
        text_width = bbox[2] - bbox[0]
        x = (image.width - text_width) / 2
        canvas.text((x, y), line, font=font, fill=(255, 255, 255, 255),
                    stroke_width=5, stroke_fill=(0, 0, 0, 255))
        # Move to the next line with some spacing
        y += bbox[3] - bbox[1] + 10

    image.save(output, 'PNG')
