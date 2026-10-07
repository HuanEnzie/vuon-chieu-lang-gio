# Inject the GPT-designed pixel textures into the page.
import json
src = open("vuon-chieu.src.html", encoding="utf-8").read()
tex = json.load(open("gpt/textures.json"))
out = src.replace("__TEXTURES__", json.dumps(tex))
open("vuon-chieu.html", "w", encoding="utf-8").write(out)
print("built", len(out) // 1024, "KB")
