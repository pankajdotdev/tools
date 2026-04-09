# 🎬 Video Editor Tool

Ek powerful command-line video editor Python script jo **ffmpeg** ki madad se kaam karta hai. Resolution change karo, videos split karo, compress karo, aur bahut kuch — sab ek hi file mein.

---

## 📦 Requirements

### Python Packages
```bash
pip install rich moviepy
```

> `rich` aur `moviepy` optional hain — inke bina bhi script kaam karegi, bas colorful output nahi milega.

### System Dependency — ffmpeg ⚠️ (Zaroori hai)

| OS | Install Command |
|----|----------------|
| **Ubuntu / Debian** | `sudo apt install ffmpeg` |
| **macOS** | `brew install ffmpeg` |
| **Windows** | [ffmpeg.org/download.html](https://ffmpeg.org/download.html) se download karo aur PATH mein add karo |

---

## 🚀 Quick Start

```bash
# Pehle info dekho apni video ka
python video_editor.py myvideo.mp4 info
```

---

## ✨ Features & Usage

### 1. 📋 Video Info
Video ki resolution, FPS, duration aur size dekho.

```bash
python video_editor.py myvideo.mp4 info
```

**Output example:**
```
Resolution : 1920 x 1080
FPS        : 30.0
Duration   : 245.30 sec
File Size  : 87.42 MB
```

---

### 2. 🔧 Resolution Change
Video ki width aur height badlo.

```bash
python video_editor.py myvideo.mp4 resolution -W 1280 -H 720 -o output_720p.mp4
```

**Common resolutions:**

| Quality | Width | Height |
|---------|-------|--------|
| 4K      | 3840  | 2160   |
| 1080p   | 1920  | 1080   |
| 720p    | 1280  | 720    |
| 480p    | 854   | 480    |
| 360p    | 640   | 360    |

---

### 3. ✂️ Split Video

#### By Size (MB) — WhatsApp/Telegram ke liye perfect
Agar video 100MB ki hai aur tum `--max-mb 30` set karo, to automatically 30MB ke parts ban jayenge.

```bash
python video_editor.py myvideo.mp4 split --max-mb 30 -o ./parts/
```

#### By Duration (seconds)
Har part ek fixed time ka hoga.

```bash
python video_editor.py myvideo.mp4 split --seconds 60 -o ./parts/
```

**Output:**
```
Part 001: myvideo_part001.mp4  (29.8 MB)
Part 002: myvideo_part002.mp4  (28.5 MB)
Part 003: myvideo_part003.mp4  (21.3 MB)
✅ 3 parts saved in: ./parts/
```

---

### 4. 🗜️ Compress Video
Video ko target size tak compress karo (2-pass encoding use hota hai best quality ke liye).

```bash
python video_editor.py myvideo.mp4 compress --target-mb 50 -o compressed.mp4
```

> ⚠️ Target size bahut chhoti mat rakho — agar video 10 minute ki hai aur 5MB target doge to quality bahut kharab ho jayegi.

---

### 5. 🎵 Audio Extract
Video se audio nikalo as MP3 (192kbps quality).

```bash
python video_editor.py myvideo.mp4 audio -o audio.mp3
```

---

### 6. ✂️ Trim Video
Video ka koi specific hissa kato — start aur end second batao.

```bash
# 30 second se lekar 1 minute 30 second tak
python video_editor.py myvideo.mp4 trim --start 30 --end 90 -o trimmed.mp4
```

---

### 7. 💧 Watermark Add
Video par text watermark lagao — position bhi choose kar sakte ho.

```bash
python video_editor.py myvideo.mp4 watermark --text "Dev © 2024" --position bottomright -o wm.mp4
```

**Position options:**
- `topleft`
- `topright`
- `bottomleft`
- `bottomright` *(default)*
- `center`

---

### 8. 🖼️ Extract Frames (Thumbnails)
Video ke frames images mein save karo.

```bash
# Har second mein se 1 frame nikalo
python video_editor.py myvideo.mp4 frames --fps 1 -o ./frames/

# Har second mein se 5 frames (slow-mo analysis ke liye)
python video_editor.py myvideo.mp4 frames --fps 5 -o ./frames/
```

---

### 9. ⚡ Speed Change
Video fast ya slow karo.

```bash
# 2x fast (time-lapse style)
python video_editor.py myvideo.mp4 speed --factor 2.0 -o fast.mp4

# 0.5x slow (slow motion)
python video_editor.py myvideo.mp4 speed --factor 0.5 -o slow.mp4
```

> ⚠️ Speed factor 0.5 se 2.0 ke beech rakho for best audio quality.

---

## 📁 Project Structure

```
video_editor.py     ← Main script (yahi run karo)
README.md           ← Yeh file
```

---

## 🧩 Full Command Reference

```
python video_editor.py <INPUT_FILE> <COMMAND> [OPTIONS]

Commands:
  info                          Video info dikhao
  resolution  -W -H -o          Resolution change karo
  split       --max-mb OR --seconds, -o    Split karo
  compress    --target-mb -o    Compress karo
  audio       -o                Audio extract karo
  trim        --start --end -o  Trim karo
  watermark   --text [--position] -o  Watermark lagao
  frames      [--fps] -o        Frames extract karo
  speed       --factor -o       Speed change karo
```

---

## 💡 Common Use Cases

| Kaam | Command |
|------|---------|
| WhatsApp pe bhejna (30MB limit) | `split --max-mb 30` |
| Telegram limit ke liye (2GB) | `compress --target-mb 1900` |
| Instagram Reels crop | `trim --start 0 --end 60` |
| Podcast audio nikalna | `audio -o podcast.mp3` |
| Video thumbnail banana | `frames --fps 0.1 -o thumbs/` |
| Old video HD mein convert | `resolution -W 1920 -H 1080` |

---

## ❓ Troubleshooting

**`ffmpeg not found` error aa raha hai?**
→ ffmpeg install karo aur PATH mein add karo. Verify karo: `ffmpeg -version`

**`pip install` ke baad bhi `rich` kaam nahi kar raha?**
→ Script bina `rich` ke bhi chalegi, bas plain text output milega.

**Split karne ke baad last part bahut chhoti hai?**
→ Yeh normal hai — remaining duration utna hi hoga.

**Compress karne ke baad size target se thoda zyada hai?**
→ 2-pass encoding estimate karta hai, exact size guarantee nahi hoti. ±5% normal hai.

---

## 👨‍💻 Author

Banaya gaya by **Dev** — ICICI Bank Operations Engineer  
Tool designed for quick video processing without GUI — pure terminal power! 🖥️