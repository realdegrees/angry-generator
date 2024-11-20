from flask import Flask, request, send_file, make_response
import os
from dotenv import load_dotenv
from io import BytesIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from image import create_image
from PIL import Image


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
@cache.cached(timeout=600, query_string=True)
def home(caption=''):
    image_type = request.args.get('type')
    extensions = ['png', 'jpg', 'jpeg', 'gif']
    image_path = None
    extension =  None
    mimetype = None
    
    for ext in extensions:
        potential_path = os.path.join('background', f'{image_type}.{ext}')
        if os.path.exists(potential_path):
            image_path = potential_path
            extension = ext
            break
    if image_path is None:
        image_path = os.path.join('background', 'default.png')


    # Save the image to a BytesIO object
    result = BytesIO()
    image_extensions = list(Image.EXTENSION.keys())
    video_extensions = None # TODO - Add video support
    if extension in image_extensions:
        image = create_image(caption, image_path)
        image.save(result, extension.upper())
        mimetype = f'image/${extension}'
    elif extension in video_extensions:
        # TODO - Implement video support
        print('Video support is not implemented yet')
   

    result.seek(0)

    # Return the image
    response = make_response(send_file(result, mimetype=mimetype, download_name=f'{caption}.{extension}'))
    # Cache for 1 hour
    response.headers['Cache-Control'] = 'public, max-age=3600'
    response.headers['Expires'] = '3600'
    return response


if __name__ == '__main__':
    app.run(debug=debug)
