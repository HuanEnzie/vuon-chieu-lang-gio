# Slice GPT-generated sheets into crisp pixel textures (sampled at cell centres) and emit data URIs.
import json, base64, io
from PIL import Image
import numpy as np

def tiles(path, n=4, inset=6):
    im = Image.open(path).convert("RGB")
    W, H = im.size
    tw, th = W / n, H / n
    out = []
    for r in range(n):
        row = []
        for c in range(n):
            box = (int(c * tw + inset), int(r * th + inset), int((c + 1) * tw - inset), int((r + 1) * th - inset))
            row.append(im.crop(box))
        out.append(row)
    return out

def pixelate(tile, cells):
    a = np.asarray(tile).astype(np.float32)
    h, w, _ = a.shape
    res = np.zeros((cells, cells, 3), np.uint8)
    for y in range(cells):
        for x in range(cells):
            y0, y1 = int((y + 0.3) * h / cells), int((y + 0.7) * h / cells) + 1
            x0, x1 = int((x + 0.3) * w / cells), int((x + 0.7) * w / cells) + 1
            res[y, x] = np.median(a[y0:y1, x0:x1].reshape(-1, 3), axis=0)
    return res

def uri(arr, mode="RGB"):
    im = Image.fromarray(arr, mode)
    b = io.BytesIO()
    im.save(b, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()

T = {}
B = tiles("blocks.png", inset=4)
names = [["grass_top", "grass_side", "dirt", "mossy"], ["planks", "log", "log_top", "bricks"],
         ["cherry", "leaves", "roof", "plaster"], ["water", "farmland", "hay", "glass"]]
for r in range(4):
    for c in range(4):
        T[names[r][c]] = uri(pixelate(B[r][c], 16))

S = tiles("skins.png", inset=8)
sk = {"face": (0, 0), "head_side": (0, 1), "head_back": (0, 2), "head_top": (0, 3),
      "shirt_front": (1, 0), "shirt_back": (1, 1), "arm": (1, 2), "legs": (1, 3),
      "face_happy": (2, 0), "face_smile": (2, 1), "jacket": (2, 2),
      "cat_face": (3, 0), "cat_fur": (3, 1), "dog_face": (3, 2), "dog_fur": (3, 3)}
pix = {}
for k, (r, c) in sk.items():
    pix[k] = pixelate(S[r][c], 32)
    T[k] = uri(pix[k])

# 3D hair shell: keep only dark hair pixels (top rows for the fringe, all rows for sides)
def hair_mask(arr, max_row):
    rgba = np.zeros((32, 32, 4), np.uint8)
    rgba[..., :3] = arr
    lum = arr.astype(np.float32) @ np.array([0.299, 0.587, 0.114])
    m = lum < 70
    m[max_row:, :] = False
    rgba[..., 3] = np.where(m, 255, 0)
    return rgba
T["hair_front"] = uri(hair_mask(pix["face"], 13), "RGBA")
T["hair_side"] = uri(hair_mask(pix["head_side"], 32), "RGBA")
json.dump(T, open("textures.json", "w"))
print({k: len(v) for k, v in T.items()})
# preview sheet
prev = Image.new("RGBA", (32 * 8 * 4, 32 * 4 * 4), (255, 0, 255, 255))
for i, (k, v) in enumerate(T.items()):
    im = Image.open(io.BytesIO(base64.b64decode(v.split(",")[1]))).convert("RGBA").resize((128, 128), Image.NEAREST)
    prev.alpha_composite(im, ((i % 8) * 128, (i // 8) * 128))
prev.save("preview.png")
