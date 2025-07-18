import os, site
import numpy as np
from moviepy.editor import *
from PIL import Image

# ✅ Windows + PIL compatibility
os.environ["IMAGEMAGICK_BINARY"] = r"C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"
site.addsitedir(r"C:\\Users\\hp\\AppData\\Roaming\\Python\\Python313\\site-packages")
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

# ✅ Constants
INPUT_DIR = "input"
OUTPUT_FILE = "output/final_output.mp4"
VIDEO_WIDTH, VIDEO_HEIGHT = 1080, 1920
IMAGE_DURATION = 1.8  # seconds per image
AMP = 25              # Amplitude: how far it shakes (pixels)
FREQ = 5              # Frequency: how fast it shakes (Hz)
OVERZOOM = 1.15       # Zoom in to avoid black edges

# ✅ Professional Shake Function with Easing and Wiggle-style Motion
def apply_pro_shake(image_clip, amp=AMP, freq=FREQ):
    W, H = image_clip.size

    def easing_envelope(t, total_duration):
        fade_time = 0.3  # ease in/out duration
        if t < fade_time:
            return t / fade_time
        elif t > total_duration - fade_time:
            return (total_duration - t) / fade_time
        else:
            return 1

    def make_frame(t):
        ease = easing_envelope(t, image_clip.duration)
        dx = amp * np.sin(2 * np.pi * freq * t + np.pi / 4) * ease
        dy = amp * np.cos(2 * np.pi * freq * t + np.pi / 3) * ease
        dx, dy = int(dx), int(dy)

        frame = image_clip.get_frame(t)
        x_start = amp + dx
        y_start = amp + dy
        x_end = x_start + VIDEO_WIDTH
        y_end = y_start + VIDEO_HEIGHT
        return frame[y_start:y_end, x_start:x_end]

    # Pad to allow safe shaking
    padded_clip = image_clip.crop(
        x_center=W // 2,
        y_center=H // 2,
        width=VIDEO_WIDTH + amp * 2,
        height=VIDEO_HEIGHT + amp * 2
    )

    return VideoClip(make_frame=make_frame, duration=image_clip.duration).set_fps(30)

# ✅ Load and process all images
image_clips = []
for filename in sorted(os.listdir(INPUT_DIR)):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        path = os.path.join(INPUT_DIR, filename)
        img = Image.open(path)
        img_w, img_h = img.size

        scale_w = (VIDEO_WIDTH * OVERZOOM) / img_w
        scale_h = (VIDEO_HEIGHT * OVERZOOM) / img_h
        scale = max(scale_w, scale_h)

        img_clip = (
            ImageClip(path)
            .resize(scale)
            .set_duration(IMAGE_DURATION)
        )

        shaken_clip = apply_pro_shake(img_clip)
        image_clips.append(shaken_clip)

# ✅ Combine all clips
final_video = concatenate_videoclips(image_clips, method="compose")
final_video.write_videofile(OUTPUT_FILE, fps=30, preset="ultrafast")
