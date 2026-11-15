
from PIL import Image, ImageDraw, ImageFont
import subprocess
import os

# Video settings
WIDTH, HEIGHT = 1280, 720
OUTPUT_DIR = "generated_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Create a dusty-pink educational title card
image = Image.new("RGB", (WIDTH, HEIGHT), "#e8b9c5")
draw = ImageDraw.Draw(image)

# Background decoration
draw.ellipse((850, -180, 1450, 420), fill="#d995a8")
draw.ellipse((-200, 480, 400, 1080), fill="#d995a8")

# Fonts
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
title_font = ImageFont.truetype(font_path, 64)
subtitle_font = ImageFont.truetype(font_path, 30)

# Text
title = "WHAT IF YOUR HEART"
subtitle = "STOPPED WORKING FOR 10 SECONDS?"

draw.text((100, 260), title, font=title_font, fill="#34242b")
draw.text((105, 355), subtitle, font=subtitle_font, fill="#34242b")

draw.text(
    (105, 610),
    "YOUR DAILY DOSE OF SCIENCE",
    font=subtitle_font,
    fill="#34242b"
)

# Save image
image_path = os.path.join(OUTPUT_DIR, "thumbnail_test.png")
image.save(image_path)

# Convert image into a short MP4 video
video_path = os.path.join(OUTPUT_DIR, "first_test.mp4")

subprocess.run([
    "ffmpeg", "-y",
    "-loop", "1",
    "-i", image_path,
    "-t", "8",
    "-r", "30",
    "-pix_fmt", "yuv420p",
    "-c:v", "libx264",
    video_path
], check=True)

print("SUCCESS! Sample educational video created.")
print(f"Video location: {video_path}")
