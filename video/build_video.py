# Assemble the film composition: reuse the garden's world/characters/shaders from the website source,
# add captions, inject the GPT-designed textures, and pre-mix the Mixkit soundtrack.
import json, re, subprocess

SITE = "../vuon-chieu.src.html"
src = open(SITE, encoding="utf-8").read()

def between(a, b):
    i = src.index(a)
    j = src.index(b, i)
    return src[i:j]

scene_a = between("  /* ============================ TEXTURES", "  // brand mark: the owner's GPT face")
scene_b = between("  /* ============================ SKY + POST-PROCESSING", "  /* ============================ INTERACTION")
scene = (scene_a + scene_b).replace("const TEX = __TEXTURES__;", "const TEX = " + json.dumps(json.load(open("../gpt/textures.json"))) + ";")
# the film is a fixed 1920x1080 frame: full quality path
scene = scene.replace("const LOW = isPhone();", "const LOW = false;")
# Math.random is replaced by a seeded generator at the top of the film module; call it through that name
scene = scene.replace("Math.random()", "seededRandom()")

CAPTIONS = [
    ("cap1", 8.0, 11.9, "Năm giờ chiều, nắng đã dịu."),
    ("cap2", 12.6, 17.4, "Mình xách bình ra tưới rau."),
    ("cap3", 17.8, 22.6, "Con thỏ lại lén gặm cà rốt. Mình giả vờ không thấy."),
    ("cap4", 23.4, 28.4, "Hai cô gà mái có quả trứng đầu tiên."),
    ("cap5", 28.9, 32.4, "Mochi chẳng chịu ngồi yên bao giờ."),
    ("cap6", 32.8, 37.8, "Còn Mướp thì ngủ quên trên ghế gỗ."),
    ("cap7", 40.0, 45.2, "Tiếng nước nhỏ thôi, mà cả buổi chiều dịu hẳn."),
    ("cap8", 47.0, 52.0, "Rồi đèn lên, đom đóm bay ra từ bụi cỏ."),
    ("cap9", 52.6, 55.6, "Có những ngày chẳng cần làm gì."),
]
cap_html = "\n".join(
    f'      <div id="{cid}" class="layer bottom clip" data-start="{s}" data-duration="{round(e - s, 2)}" data-track-index="2">'
    f'<div id="{cid}-in" class="panel cap">{text}</div></div>'
    for cid, s, e, text in CAPTIONS
)
cap_times = json.dumps([{"id": c, "start": s, "end": e} for c, s, e, _ in CAPTIONS])

tpl = open("src/film.tpl.html", encoding="utf-8").read()
fonts = open("assets/fonts/fonts.css", encoding="utf-8").read()
out = (tpl.replace("/*__FONTS__*/", fonts)
          .replace("      __CAPTIONS__", cap_html)
          .replace("__CAPTION_TIMES__", cap_times)
          .replace("      //__SCENE__", scene))
open("index.html", "w", encoding="utf-8").write(out)
print("index.html", len(out) // 1024, "KB")

# ---- soundtrack pre-mix (all sources from Mixkit, see CREDITS.md)
A = "assets/audio/"
inputs = [
    ("bgm-sleepy-cat-135.mp3", 0.0, "atrim=0:60,volume=0.62,afade=t=in:d=1.5,afade=t=out:st=55.5:d=4.5"),
    ("amb-birds-river-2473.mp3", 0.0, "atrim=0:50,volume=0.16,afade=t=in:d=2,afade=t=out:st=44:d=5"),
    ("amb-night-crickets-1789.mp3", 45.0, "atrim=0:15,volume=0.22,afade=t=in:d=4,afade=t=out:st=11:d=4"),
    ("amb-water-flow-3126.mp3", 12.4, "atrim=0:8.6,volume=0.1,afade=t=in:d=0.8,afade=t=out:st=7.4:d=1.2"),
    ("sfx-chicken-1772.mp3", 26.5, "volume=0.32"),
    ("sfx-puppy-bark-741.mp3", 29.55, "atrim=0:1.5,volume=0.28,afade=t=out:st=1.1:d=0.4"),
    ("sfx-cat-meow-93.mp3", 35.75, "volume=0.42"),
    ("sfx-water-splash-1311.mp3", 42.5, "volume=0.26"),
    ("sfx-water-splash-1311.mp3", 44.0, "volume=0.22"),
    ("sfx-water-splash-1311.mp3", 45.3, "volume=0.24"),
]
args = ["ffmpeg", "-v", "error", "-y"]
for f, _, _ in inputs:
    args += ["-i", A + f]
chains = []
for i, (_, start, flt) in enumerate(inputs):
    ms = int(start * 1000)
    chains.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,{flt},adelay={ms}|{ms}[a{i}]")
mix = "".join(f"[a{i}]" for i in range(len(inputs)))
chains.append(f"{mix}amix=inputs={len(inputs)}:normalize=0,atrim=0:60,alimiter=limit=0.9[out]")
args += ["-filter_complex", ";".join(chains), "-map", "[out]", "-ac", "2", "-ar", "48000", A + "soundtrack.wav"]
subprocess.run(args, check=True)
print("soundtrack.wav ok")
