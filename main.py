from flask import Flask, request, send_file, make_response
import os
from dotenv import load_dotenv
from io import BytesIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from image import create_image

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


@app.route('/')
@app.route('/<caption>', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def home(caption=''):
    image_type = request.args.get('type')
    image_path = os.path.join('emojis', f'{image_type}.png')
    if not os.path.exists(image_path):
        image_path = os.path.join('emojis', 'default.png')

    image = create_image(caption, image_path)
    # Save the  image to a BytesIO object
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
