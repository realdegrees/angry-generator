
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
from util import load_font, process_caption


def create_video(caption, video_path):
    video = VideoFileClip(video_path)
    caption = process_caption(caption)
    font_path, font_size = load_font()

    text_clip = TextClip(caption, method=caption, font=font_path, fontsize=font_size,
                         color='white', stroke_color='black', stroke_width=5, duration=video.duration,
                         size=video.size[0], text_align='center', vertical_align='top', horizontal_align='center', margin=10)

    video = CompositeVideoClip([video, text_clip])
    return video
