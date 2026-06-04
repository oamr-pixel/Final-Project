import cv2, random
import numpy as np

# 7 small video clips I found online all under 10 secs long, to get many scenes to look at
# took a couple hours to run all of them bc the frame rates were all somewhere 70-120
# and the painting process was very slow, but I was able to generate better looking results
# also some of the videos improved since I recorded the presentation
# so some of the videos I included in this folder look better than the ones in the presentation, hope that is fine
# also some of the output videos are shorter than the input bc of the max frame limit

ins = [
    "16166-269541539.mp4",
   "35427-407130886_medium.mp4",
 "49779-459795216_medium.mp4",
  "3904-175596530_medium.mp4",
  "335486_medium.mp4",
 "94459-643067832_medium.mp4",
 "93480-640562082_medium.mp4"
]

outs = [
    "painted_video1.mp4",
 "painted_video2.mp4",
   "painted_video3.mp4",
  "painted_video4.mp4",
 "painted_video5.mp4",
 "painted_video6.mp4",
   "painted_video7.mp4"
]

# smaller frames & fewer frames so this can actually run, I set max at 120 frames
scale = 0.45
maxf = 2
ofps = 12

# From Hertzmann, big strokes first, then smaller details
rads = [8, 4, 2]
blur = 0.5
grid = 0.85

# repaints only if the painting is wrong enough
it = 18

# repaint only if the video changed enough
# this is the temporal coherence part
vt = 8

# short strokes looked better for videos & borders, adjusted these vals and best came from these
minl = 1
maxl = 3
curve = 0.75

alpha = 0.92
blend = 0.08

def size(f):
    # shrink every frame first, full resolution was wayyyyyy too slow
    h, w = f.shape[:2]
    return cv2.resize(f,(int(w * scale), int(h * scale)), 
                      interpolation=cv2.INTER_AREA
    )

def diff(a, b):
    # error image showing where two images are different
    d = a.astype(np.float32) - b.astype(np.float32)
    return np.sqrt(np.sum(d * d, axis=2))

def dist(a, b):
    # same thing, but for one pixel
    d = a.astype(np.float32) - b.astype(np.float32)
    return float(np.sqrt(np.sum(d * d)))

def grad(img):
    # had strokes move perpendicular to the gradient so they follow contours
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.sqrt(gx * gx + gy * gy)
    return gx, gy, mag

#makes strokes
def stroke(x, y, r, ref, can, gx, gy, mag):
    h, w = ref.shape[:2]

    x = int(np.clip(x, 0, w - 1))
    y = int(np.clip(y, 0, h - 1))

    col = ref[y, x].copy()
    pts = [(x, y)]
    lx, ly = 0.0, 0.0

    for i in range(maxl):
        xi = int(np.clip(round(x), 0, w - 1))
        yi = int(np.clip(round(y), 0, h - 1))

        # stop if this stroke is not helping anymore
        if i > minl:
            if dist(ref[yi, xi], can[yi, xi]) < dist(ref[yi, xi], col):
                break

        if mag[yi, xi] < 1e-3:
            break

        # Hertzmann curved stroke 
        dx, dy = -gy[yi, xi], gx[yi, xi]

        n = np.sqrt(dx * dx + dy * dy)
        if n < 1e-6:
            break

        dx, dy = dx / n, dy / n

        # avoid random direction flips
        if lx * dx + ly * dy < 0:
            dx, dy = -dx, -dy

        # smooth the curve
        dx = curve * dx + (1 - curve) * lx
        dy = curve * dy + (1 - curve) * ly

        n = np.sqrt(dx * dx + dy * dy)
        if n < 1e-6:
            break

        dx, dy = dx / n, dy / n

        x += r * dx
        y += r * dy

        # stop strokes at the border
        if x < 0 or x >= w or y < 0 or y >= h:
            break

        pts.append((int(round(x)), int(round(y))))
        lx, ly = dx, dy

    return pts, col, r

# draws stroke onto the canvas /w alpha blending
def draw(can, s):
    pts, col, r = s
    over = can.copy()

    if len(pts) == 1:
        cv2.circle(over, pts[0], max(1, int(r)), col.tolist(), -1, lineType=cv2.LINE_AA)
    else:
        arr = np.array(pts, dtype=np.int32).reshape((-1, 1, 2))

        cv2.polylines(
            over,
            [arr],
            False,
            col.tolist(),
            thickness=max(1, int(2 * r)),
            lineType=cv2.LINE_AA
        )

        # fills iin the path so it looks more like paint
        for p in pts:
            cv2.circle(over, p, max(1, int(r)), col.tolist(), -1, lineType=cv2.LINE_AA)

    cv2.addWeighted(over, alpha, can, 1 - alpha, 0, can)

# paints a layer of strokes, then returns the new canvas
def layer(can, ref, r, vdiff=None, force=False):
    h, w = ref.shape[:2]

    gx, gy, mag = grad(ref)
    err = diff(can, ref)

    step = max(1, int(grid * r))
    strokes = []

    for y in range(0, h, step):
        for x in range(0, w, step):
            y0 = max(0, y - step // 2)
            y1 = min(h, y + step // 2 + 1)
            x0 = max(0, x - step // 2)
            x1 = min(w, x + step // 2 + 1)

            box = err[y0:y1, x0:x1]
            perr = box.mean()

            if vdiff is None:
                verr = 999.0
            else:
                verr = vdiff[y0:y1, x0:x1].mean()

            # only repaint places that changed &  still look wrong
            if force or (verr > vt and perr > it):
                yy, xx = np.unravel_index(np.argmax(box), box.shape)
                px, py = x0 + xx, y0 + yy
                strokes.append(stroke(px, py, r, ref, can, gx, gy, mag))

    # Hertzmann said random order hides the grid pattern
    random.shuffle(strokes)

    for s in strokes:
        draw(can, s)

    return can

def paint(f, prev=None, raw=None):
    first = prev is None or raw is None

    if first:
        # first frame starts from a blank canvas
        can = np.zeros_like(f)
        can[:] = f.reshape(-1, 3).mean(axis=0)
        vdiff = None
    else:
        # temporal coherence
        # reuse the last painted frame instead of repainting from scratch
        can = prev.copy()

        # only repaint where the raw video actually changed
        vdiff = diff(f, raw)

        # ignore tiny noise so the strokes do not flicker everywhere
        vdiff = cv2.GaussianBlur(vdiff, (0, 0), 1.2)

    # Hertzmann approach for layers, so big strokes first, smaller ones refine it, same as earlier
    for r in rads:
        sig = blur * r

        ref = cv2.GaussianBlur(
            f,
            (0, 0),
            sigmaX=sig,
            sigmaY=sig
        )

        can = layer(
            can,
            ref,
            r,
            vdiff=vdiff,
            force=first
        )

    # keeps some real detail from the og frame
    can = cv2.addWeighted(can, 1 - blend, f, blend, 0)

    return can

def run(inp, out):
    cap = cv2.VideoCapture(inp)

    fps = cap.get(cv2.CAP_PROP_FPS)

    

    # skip frames bc the clips had high fps
    skip = max(1, int(round(fps / ofps)))
    fout = fps / skip

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    total = min(max(1, total // skip), maxf)

    ret, f = cap.read()

    if not ret:
        cap.release()
        return

    # only use first frame to get output size
    first = size(f)
    h, w = first.shape[:2]

    writer = cv2.VideoWriter(
        out,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fout,
        (w, h)
    )

    raw = None
    prev = None

    outc = 0
    inc = 0

    while outc < total:
        if inc % skip == 0:
            small = size(f)

            painted = paint(
                small,
                prev,
                raw
            )

            writer.write(painted)

            # raw frame checks motion
            # painted frame becomes the next canvas
            raw = small.copy()
            prev = painted.copy()

            outc += 1

        ret, f = cap.read()

        if not ret:
            break

        inc += 1

    cap.release()
    writer.release()

# processes each video
for inp, out in zip(ins, outs):
    run(inp, out)