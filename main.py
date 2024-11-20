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

# ! this loads the file from disk on every non-cached request, this could be optimized to load files on startup but would break hots-swapping of files
@app.route('/')
@app.route('/<caption>', methods=['GET'])
@cache.cached(timeout=600, query_string=True)
def home(caption=''):
    image_type = request.args.get('type') or os.getenv(
        'DEFAULT', 'default')

    path = None
    extension = None

    # Check if the requested image exists and set the path, filename, and extension if it does
    files = glob.glob(os.path.join('background', f'{image_type}.*'))
    if files:
        path = files[0]
        filename = os.path.splitext(os.path.basename(path))[0]
        extension = os.path.splitext(path)[1][1:]
        
    else:
        path = os.path.join('background', f'default.png')
        filename = 'default.png'
        extension = 'png'
        if not os.path.exists(path):
            return make_response("There was an issue loading the image. Please contact the admin if the issue persists.", 404)

    # Audio
    
    ## Build path
    audio_arg = request.args.get("audio", filename)
    audio_path = f'audio/{audio_arg}.ogg'
    
    ## Check conditions
    disable_audio = audio_arg.lower() in ["off", "mute", "none", "false"]
    audio_exists = os.path.exists(audio_path)
    if disable_audio or not audio_exists:
        audio_path = None

    # Create an object to store the result in memory
    output = BytesIO()

    # Fill the output via the appropriate pipeline
    if extension in image_extensions:
        if audio_path:
            create_video(caption, path, extension, output, audio_path)
            mimetype = 'video/webm'
        else:
            create_image(caption, path, extension, output)
            mimetype, _ = 'image/gif'
    elif extension in video_extensions:
        create_video(caption, path, extension, output, audio_path)
        mimetype = 'video/webm'



    # Build response
    output.seek(0)
    response = make_response(
        send_file(output, mimetype=mimetype, download_name=f'{caption}.{extension}'))
    response.headers['Content-Type'] = mimetype
    response.headers['Cache-Control'] = f'public, max-age={60 * 60 * 24}'
    response.headers['Expires'] = f'{60 * 60 * 24}'
    
    return response


if __name__ == '__main__':
    app.run(debug=debug)
