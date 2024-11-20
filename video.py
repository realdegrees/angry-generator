
from io import BytesIO
from moviepy import VideoFileClip, AudioFileClip, ImageClip, TextClip, CompositeVideoClip, vfx
from util import get_supported_video_formats, load_font, process_caption
import tempfile
import os
from PIL import Image

image_extensions = [ext.lower().replace('.', '')
                    for ext in list(Image.registered_extensions())]
video_extensions = get_supported_video_formats()

def create_video(caption: str, file_path: str, extension: str, output: BytesIO, audio_path: str = None):
    caption = process_caption(caption)
    font_path, font_size = load_font(caption)

    # Audio
    audio = AudioFileClip(audio_path)

    # Video
    if extension not in video_extensions and extension in image_extensions:
        video = ImageClip(file_path, duration=audio.duration)
    else:
        video: VideoFileClip = VideoFileClip(file_path)
        if audio_path:
            video = video.with_effects([vfx.Loop(duration=audio.duration)])
    
    
    # Text
    margin = 50
    text: TextClip = TextClip(text=caption, method='caption', font=font_path, font_size=round(font_size * 3/4), bg_color='rgba(0,0,0,0)',
                    color='white', stroke_color='black', stroke_width=3, duration=audio.duration if audio_path else video.duration,
                              size=(round(video.size[0] - 2 * margin), None), margin=(margin, margin, margin, 0), text_align='center', vertical_align='top', horizontal_align='center').with_fps(1)

    # Combine video and text
    combined_adjusted_height = round(video.size[1] * 1) + text.size[1]
    size = (video.size[0], combined_adjusted_height)
     # Set masks
    video = video.with_mask(video.mask)
    text = text.with_mask(text.mask)
    
    # Set Positions
    video = video.with_position(('center', 'bottom'))
    text = text.with_position(('center', 'top'))

    composite: CompositeVideoClip = CompositeVideoClip([video, text], size)
    composite = composite.with_audio(audio)
    
    # Set codecs
    video_codec = 'libvpx-vp9'
    audio_codec = 'libvorbis'

        
    # Create Debug Video
    debug_file_path = os.path.join(
        os.path.dirname(__file__), f'debug/latest.webm')
    composite.write_videofile(debug_file_path, codec=video_codec,
                              logger=None, audio_codec=audio_codec)
    
    
    # Create temp file to save the clip
    prefix = caption.replace(' ', '_').lower()
    with tempfile.NamedTemporaryFile(delete=False, prefix=prefix, suffix='.webm') as temp_file:
        temp_path = temp_file.name

    # Write clip to temp file
    composite.write_videofile(temp_path, codec=video_codec,
                              logger=None, audio_codec=audio_codec)

    # Write the file content to the io object and remove the temp file
    with open(temp_path, 'rb') as temp_file:
        output.write(temp_file.read())
    os.remove(temp_path)
