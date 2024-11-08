from flask import Flask, request, send_file
import os
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

load_dotenv()
env = os.getenv('ENV', 'development')
debug = env == 'development'
app = Flask(__name__)


@app.route('/', defaults={'path': ''})
@app.route('/<caption>', methods=['GET'])
def home(caption):
    image_type = request.args.get('type')
    image_path = os.path.join('emojis', f'{image_type}.png')
    if not os.path.exists(image_path):
        image_path = os.path.join('emojis', 'default.png')

    # Load the image
    image = Image.open(image_path)

    # Initialize ImageDraw
    draw = ImageDraw.Draw(image)

    # Load a font
    font = request.args.get('font', 'impact')
    font_size = int(request.args.get('font_size', '170'))
    font_path = os.path.join('fonts', f'{font}.ttf')
    try:
        font = ImageFont.truetype(font_path, font_size)
    except OSError:
        font = ImageFont.load_default(font_size)

    # Generate image
    caption = caption.capitalize()
    print(caption)
    if caption.lower().endswith('.gif'):
        caption = caption[:-4]

    # Calculate text size and position
    bbox = draw.textbbox((0, 0), caption, font=font, spacing=0, stroke_width=4)
    text_width = bbox[2] - bbox[0]
    x = (image.width - text_width) / 2
    y = 20

    # Draw text with stroke
    draw.text((x, y), caption, font=font, fill=(255, 255, 255, 255), stroke_width=5, stroke_fill=(0, 0, 0, 255))

    # Save the edited image to a BytesIO object
    img_io = BytesIO()
    image.save(img_io, 'GIF')   
    img_io.seek(0)

    # Return the image
    return send_file(img_io, mimetype='image/gif')


if __name__ == '__main__':
    app.run(debug=debug)
