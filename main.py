from flask import Flask, request, send_file, make_response
import os
from dotenv import load_dotenv
from io import BytesIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from image import create_image
from video import create_video
from PIL import Image
from util import get_supported_video_formats
import mimetypes

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

# List of supported file extensions
image_extensions = list(Image.EXTENSION.keys())
video_extensions = get_supported_video_formats()
supported_extensions = image_extensions + video_extensions

# ! this loads the file from disk on every non-cached request, this could be optimized to load files on startup but would break hots-swapping of files
@app.route('/')
@app.route('/<caption>', methods=['GET'])
@cache.cached(timeout=600, query_string=True)
def home(caption=''):
    image_type = request.args.get('type')
    path = None
    extension =  None
    
    for ext in supported_extensions:
        potential_path = os.path.join('background', f'{image_type}.{ext}')
        if os.path.exists(potential_path):
            path = potential_path
            extension = ext
            break
    if path is None:
        path = os.path.join('background', 'default.png')

    # Create an object to store the result in memory
    result = BytesIO()
    
    if extension in image_extensions:
        image = create_image(caption, path)
        image.save(result, extension.upper())
    elif extension in video_extensions:
        video = create_video(caption, path)
        video.write_videofile(result, codec="libx264", logger=None)
   
    result.seek(0)
    mimetype, _ = mimetypes.guess_type(path)

    # Return the file 
    response = make_response(send_file(result, mimetype=mimetype, download_name=f'{caption}.{extension}'))
    # Cache for 1 hour on the client side to reduce server load
    response.headers['Cache-Control'] = 'public, max-age=3600'
    response.headers['Expires'] = '3600'
    return response


if __name__ == '__main__':
    app.run(debug=debug)
