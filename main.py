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
import glob

load_dotenv()
env = os.getenv('ENV', 'development')
debug = env == 'development'
app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour",
                    "10 per minute", "2 per second"],
    storage_uri="memory://",
)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# List of supported file extensions
image_extensions = [ext.lower().replace('.', '')
                    for ext in list(Image.registered_extensions())]
video_extensions = get_supported_video_formats()
supported_extensions = image_extensions + video_extensions


class FileInfo:
    def __init__(self, path, extension, filename):
        self.path = path
        self.extension = extension
        self.filename = filename


def get_file_info(folder, name):
    files = glob.glob(os.path.join(folder, f'{name}.*'))
    if files:
        path = files[0]
        filename = os.path.splitext(os.path.basename(path))[0]
        extension = os.path.splitext(path)[1][1:]
        return FileInfo(path, extension, filename)
    return None

# ! this loads the file from disk on every non-cached request, this could be optimized to load files on startup but would break hots-swapping of files


@app.route('/')
@app.route('/<caption>', methods=['GET'])
@cache.cached(timeout=600, query_string=True)
def home(caption=''):
    # Load image
    _image = request.args.get('type') or os.getenv(
        'DEFAULT', 'default')
    image = get_file_info('images', _image)
    if image is None:
        return make_response("There was an issue loading the image. Please contact the admin if the issue persists.", 404)

    # Check audio conditions
    _audio = request.args.get('audio', image.filename)
    disable_audio = _audio.lower() in ["off", "mute", "none", "false"]
    if not disable_audio:
        audio = get_file_info('audio', _audio)

    # Check background conditions
    _background = request.args.get('background', image.filename)
    disable_background = _audio.lower() in ["off", "mute", "none", "false"]
    if not disable_background:
        background = get_file_info('backgrounds', _background)

    # Create an object to store the result in memory
    output = BytesIO()

    if (image.extension in video_extensions or background and background.extension in video_extensions) or audio:
        create_video(caption, image.path, image.extension, output, audio.path, background.path)
        mimetype = 'video/webm'
    else:
        create_image(caption, image.path, image.extension, output)
        mimetype = 'image/gif'
    
    # Build response
    output.seek(0)
    response = make_response(
        send_file(output, mimetype=mimetype, download_name=f'{caption}.{image.extension}'))
    response.headers['Content-Type'] = mimetype
    response.headers['Cache-Control'] = f'public, max-age={60 * 60 * 24}'
    response.headers['Expires'] = f'{60 * 60 * 24}'

    return response


if __name__ == '__main__':
    app.run(debug=debug)
