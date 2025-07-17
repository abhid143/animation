import os, site
import numpy as np
from moviepy.editor import *
from PIL import Image

# Setup
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
site.addsitedir(r"C:\\Users\\hp\\AppData\\Roaming\\Python\\Python313\\site-packages")
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

# Config
VIDEO_SIZE = (1080, 1920)
AUDIO_FILE = "assets/bg_music.mp3"
IMAGE_DIR = "input"
OUTPUT_FILE = "output/final_output.mp4"
FADE_DURATION = 0.3

ANIMATIONS = [
    "bounce", "pan", "zoom", "rotate", "shake",
    "zoom", "rotate", "pan", "shake", "bounce"
]

DURATIONS = [
    0.77, 0.86, 0.87, 0.83, 0.80,
    1.04, 0.66, 0.90, 0.77, 0.70
]

# Helpers
def force_cover_and_crop(clip):
    scale = max(VIDEO_SIZE[0] / clip.w, VIDEO_SIZE[1] / clip.h)
    clip = clip.resize(scale)
    return clip.crop(width=VIDEO_SIZE[0], height=VIDEO_SIZE[1], x_center=clip.w / 2, y_center=clip.h / 2)

# Slide-in with bounce near center
def slide_in_with_bounce(clip, direction, duration):
    def position(t):
        t_norm = np.clip(t / duration, 0, 1)
        progress = (1 - t_norm) * (VIDEO_SIZE[0] + clip.w)

        # X motion
        x = -progress if direction == "left" else VIDEO_SIZE[0] + progress - clip.w

        # Bounce near center
        center_x = (VIDEO_SIZE[0] - clip.w) / 2
        if abs(x - center_x) < 100:
            x += np.sin(t * 20) * 20  # bounce effect

        y = (VIDEO_SIZE[1] - clip.h) / 2
        return x, y

    return clip.set_position(position)

def bounce_effect(clip):
    return clip.set_position(lambda t: (540 + np.sin(10 * t) * 30, 960))

def pan_up_effect(clip, duration):
    return clip.set_position(lambda t: (540, 1920 - (t / duration) * 1920))

def zoom_effect(clip, duration):
    return clip.resize(lambda t: 1 + 0.2 * t / duration)

def rotate_effect(clip, duration):
    zoomed = clip.resize(1.2)
    rotated = zoomed.rotate(lambda t: 5 * np.sin(2 * np.pi * t / duration), resample='bilinear')
    return CompositeVideoClip([rotated.set_position("center")], size=VIDEO_SIZE).set_duration(duration)

def shake_effect(clip, strength=20, freq=20):
    def shaker(t):
        np.random.seed(int(t * freq))
        dx = np.random.uniform(-strength, strength)
        dy = np.random.uniform(-strength, strength)
        return 540 + dx, 960 + dy
    return clip.set_position(shaker)

# Animate 1 image
def animate_clip(path, index):
    duration = DURATIONS[index]
    anim = ANIMATIONS[index]
    direction = "left" if index % 2 == 0 else "right"

    clip = ImageClip(path).set_duration(duration)
    clip = force_cover_and_crop(clip)

    # Slide-in with bounce near center
    slide_clip = slide_in_with_bounce(clip, direction, duration)

    # Apply effect
    if anim == "bounce":
        animated = bounce_effect(slide_clip)
    elif anim == "pan":
        animated = pan_up_effect(slide_clip, duration)
    elif anim == "zoom":
        animated = zoom_effect(slide_clip, duration)
    elif anim == "rotate":
        animated = rotate_effect(slide_clip, duration)
    elif anim == "shake":
        animated = shake_effect(slide_clip)
    else:
        animated = slide_clip

    return animated.fadein(FADE_DURATION).fadeout(FADE_DURATION)

# Load all images
image_files = [f"{IMAGE_DIR}/{i}.jpg" for i in range(1, 11)]
clips = [animate_clip(path, idx) for idx, path in enumerate(image_files)]

# Combine
final = concatenate_videoclips(clips, method="compose")

# Add music
if os.path.exists(AUDIO_FILE):
    audio = AudioFileClip(AUDIO_FILE).subclip(0, final.duration)
    final = final.set_audio(audio)

# Export
os.makedirs("output", exist_ok=True)
final.write_videofile(OUTPUT_FILE, fps=30, codec="libx264", audio_codec="aac", preset="fast")
