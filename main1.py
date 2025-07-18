import os, site
import numpy as np
from moviepy.editor import *
from PIL import Image

# Setup for Windows + PIL compatibility
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
site.addsitedir(r"C:\\Users\\hp\\AppData\\Roaming\\Python\\Python313\\site-packages")
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

# Constants
INPUT_DIR = "input"
OUTPUT_FILE = "output/final_output.mp4"
ASSETS_DIR = "assets"
RESOLUTION = (1080, 1920)  # Shorts / TikTok resolution
DURATION = 1.2  # seconds per image
FPS = 30

def fast_zoom_effect(image_path, duration):
    clip = ImageClip(image_path).set_duration(duration)

    # Resize while preserving aspect ratio and crop to fill 1080x1920
    clip = clip.resize(height=RESOLUTION[1])
    if clip.w < RESOLUTION[0]:
        clip = clip.resize(width=RESOLUTION[0])
    clip = clip.crop(width=RESOLUTION[0], height=RESOLUTION[1], x_center=clip.w/2, y_center=clip.h/2)

    # Super fast zoom in and zoom out (scale up/down)
    def zoom(t):
        half = duration / 2
        if t < half:
            return 1.0 + 0.6 * (t / half)  # Zoom in fast
        else:
            return 1.6 - 0.6 * ((t - half) / half)  # Zoom out fast

    clip = clip.fx(vfx.resize, zoom).set_position("center").set_fps(FPS)
    return clip

# Load images
image_files = sorted([os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.endswith(".jpg")])
clips = [fast_zoom_effect(img, DURATION) for img in image_files]

# Concatenate all image clips
final_video = concatenate_videoclips(clips, method="compose")

# Add background music (cut to duration)
audio_clip = AudioFileClip(os.path.join(ASSETS_DIR, "bg_music.mp3")).subclip(0, final_video.duration)
final_video = final_video.set_audio(audio_clip)

# Export final video
final_video.write_videofile(
    OUTPUT_FILE,
    fps=FPS,
    codec="libx264",
    audio_codec="aac",
    preset="ultrafast"
)
