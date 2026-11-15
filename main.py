
import os
import subprocess
import asyncio
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import edge_tts

W, H = 1280, 720
OUT = Path("generated_videos")
OUT.mkdir(exist_ok=True)

BG = "#171116"
PINK = "#d98da5"
LIGHT = "#f4dce4"
WHITE = "#fff4f7"

SCENES = [
    {
        "title": "YOUR HEART NEVER RESTS",
        "caption": "Every beat keeps blood moving.",
        "voice": "Your heart works continuously, pumping blood throughout your body.",
        "type": "heart"
    },
    {
        "title": "A POWERFUL RHYTHM",
        "caption": "Electrical signals control each heartbeat.",
        "voice": "Electrical signals help coordinate every heartbeat. This rhythm is essential for normal heart function.",
        "type": "pulse"
    },
    {
        "title": "WHEN RHYTHM CHANGES",
        "caption": "Blood flow can be affected.",
        "voice": "If the heart rhythm becomes seriously disturbed, blood flow to important organs can be affected.",
        "type": "rings"
    },
    {
        "title": "EVERY BEAT MATTERS",
        "caption": "Your body depends on a healthy heart.",
        "voice": "Your heart is vital. If someone experiences chest pain, fainting or difficulty breathing, seek emergency medical help.",
        "type": "heart"
    }
]

def get_font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(
        f"/usr/share/fonts/truetype/dejavu/{name}", size
    )

def draw_scene(index, scene):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    d.ellipse((760, -250, 1450, 440), fill="#38202c")
    d.ellipse((-300, 470, 430, 1100), fill="#2a1a24")

    for i in range(55):
        x = (i * 197 + index * 83) % W
        y = (i * 113 + index * 47) % H
        d.ellipse((x, y, x+3, y+3), fill="#754457")

    cx, cy = 950, 350

    if scene["type"] == "heart":
        d.ellipse((cx-130, cy-100, cx, cy+60), fill=PINK)
        d.ellipse((cx, cy-100, cx+130, cy+60), fill=PINK)
        d.polygon(
            [(cx-130, cy-20), (cx+130, cy-20), (cx, cy+190)],
            fill=PINK
        )
        d.arc((cx-190, cy-210, cx+190, cy+220),
              190, 350, fill=LIGHT, width=5)

    elif scene["type"] == "pulse":
        points = [
            (720, 360), (800, 360), (850, 270),
            (900, 470), (960, 220), (1010, 360), (1150, 360)
        ]
        d.line(points, fill=PINK, width=13, joint="curve")

    else:
        for radius in (75, 135, 200):
            d.ellipse(
                (cx-radius, cy-radius, cx+radius, cy+radius),
                outline=PINK, width=5
            )
        d.ellipse((cx-35, cy-35, cx+35, cy+35), fill=LIGHT)

    d.rounded_rectangle(
        (65, 100, 650, 610),
        radius=28,
        fill="#211720",
        outline="#704253",
        width=2
    )

    d.text(
        (105, 140), f"SCIENCE STORY  /  0{index+1}",
        font=get_font(22, True), fill=PINK
    )

    title_font = get_font(48, True)
    words = scene["title"].split()
    lines, line = [], ""

    for word in words:
        test = (line + " " + word).strip()
        if d.textbbox((0, 0), test, font=title_font)[2] < 490:
            line = test
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)

    y = 240
    for line in lines:
        d.text((105, y), line, font=title_font, fill=WHITE)
        y += 65

    d.text(
        (105, 440), scene["caption"],
        font=get_font(23), fill=LIGHT
    )

    d.text(
        (105, 555), "A VISUAL SCIENCE EXPLAINER",
        font=get_font(17, True), fill=PINK
    )

    path = OUT / f"scene_{index+1}.png"
    img.save(path)
    return path

async def create_voice():
    text = " ".join(scene["voice"] for scene in SCENES)
    voice = os.getenv("TTS_VOICE", "en-US-AriaNeural")
    await edge_tts.Communicate(
        text, voice
    ).save(str(OUT / "narration.mp3"))

def main():
    images = []

    for i, scene in enumerate(SCENES):
        images.append(draw_scene(i, scene))

    asyncio.run(create_voice())

    clips = []

    for i, image in enumerate(images):
        clip = OUT / f"clip_{i+1}.mp4"

        subprocess.run([
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(image),
            "-t", "6",
            "-vf",
            "zoompan=z='min(zoom+0.0007,1.05)':d=180:s=1280x720:fps=30,format=yuv420p",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            str(clip)
        ], check=True, stdout=subprocess.DEVNULL,
           stderr=subprocess.DEVNULL)

        clips.append(clip)

    concat = OUT / "clips.txt"
    concat.write_text(
        "".join(f"file '{p.resolve()}'\n" for p in clips)
    )

    silent = OUT / "silent.mp4"

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat),
        "-c", "copy",
        str(silent)
    ], check=True)

    final = OUT / "educational_video.mp4"

    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(silent),
        "-i", str(OUT / "narration.mp3"),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        str(final)
    ], check=True)

    print("SUCCESS:", final)

if __name__ == "__main__":
    main()
