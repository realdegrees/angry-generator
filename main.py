from flask import Flask, request, send_file, make_response
import os
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

load_dotenv()
env = os.getenv('ENV', 'development')
debug = env == 'development'
app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour", "10 per minute", "2 per second"],
    storage_uri="memory://",
)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

def calculate_font_size(caption, image_width, base_font_size=170):
    # Adjust the font size based on the length of the caption
    max_length = 20  # Maximum length for the base font size
    if len(caption) > max_length:
        return max(base_font_size - (len(caption) - max_length) * 5, 110)  # Ensure font size doesn't go below 20
    return base_font_size



@app.route('/')
@app.route('/<caption>', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def home(caption=''):
    image_type = request.args.get('type')
    image_path = os.path.join('emojis', f'{image_type}.png')
    if not os.path.exists(image_path):
        image_path = os.path.join('emojis', 'default.png')

    # Load the image
    image = Image.open(image_path)

    # Initialize ImageDraw
    draw = ImageDraw.Draw(image)

    # Adjust caption
    caption = caption.capitalize()
    if caption.lower().endswith('.gif'):
        caption = caption[:-4]
        
    # Load a font
    font = request.args.get('font', 'impact')
    base_font_size = int(request.args.get('font_size', '170'))
    font_size = calculate_font_size(caption, image.width, base_font_size)
    font_path = os.path.join('fonts', f'{font}.ttf')
    try:
        font = ImageFont.truetype(font_path, font_size)
    except OSError:
        font = ImageFont.load_default(font_size)



    # Split text into multiple lines if it exceeds 90% of the image width
    max_width = image.width * 0.9
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

    # Draw each line of text
    y = 20
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=4)
        text_width = bbox[2] - bbox[0]
        x = (image.width - text_width) / 2
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255), stroke_width=5, stroke_fill=(0, 0, 0, 255))
        y += bbox[3] - bbox[1] + 10  # Move to the next line with some spacing

    # Save the edited image to a BytesIO object
    img_io = BytesIO()
    image.save(img_io, 'GIF')   
    img_io.seek(0)

    # Return the image
    response = make_response(send_file(img_io, mimetype='image/gif', download_name=f'{caption}.gif'))
    # Cache for 1 hour
    response.headers['Cache-Control'] = 'public, max-age=3600'
    response.headers['Expires'] = '3600'
    return response


if __name__ == '__main__':
    app.run(debug=debug)
