#!/usr/bin/env python3
"""
Creates slideshow.mp4 from images 1-6.jpg with blur-morph transitions.

Transition effect:
  - The two images are linearly crossfaded (blended).
  - A single Gaussian blur is applied to the composite frame.
  - Blur radius follows a sine arch: 0 → peak → 0 over the transition,
    so the scene blurs out at the midpoint and re-sharpens as the next
    image resolves — a "blurring morph" rather than two separate fades.

First image: blur-fade-in (blur + opacity + slight downward slide).
Last image:  blur-fade-out (mirror of fade-in).
"""
import math
import os
import sys
import subprocess
import numpy as np
from PIL import Image, ImageFilter

# --- Timing ---
FADE_SEC  = 0.5    # s — duration of first/last image fade-in/out
MORPH_SEC = 0.5    # s — duration of blur-morph between images
HOLD_SEC  = 2.5    # s — hold time at full quality per image
FPS       = 30

# --- Blur ---
FADE_BLUR = 8.0    # px — peak blur during fade-in / fade-out
MORPH_BLUR = 35.0  # px — peak blur at the midpoint of each morph transition

# --- Slide offset (blur-fade.svelte: direction="down", offset=6) ---
Y_OFFSET = 6       # px — vertical slide on first image fade-in

IMAGE_DIR = "assets/src/files"
OUTPUT    = "assets/src/files/slideshow.mp4"


# --- Easing ---

def ease_out(t: float) -> float:
    """Sine ease-out: fast start, smooth deceleration."""
    return math.sin(t * math.pi / 2)

def ease_in(t: float) -> float:
    """Sine ease-in: smooth acceleration, fast finish."""
    return 1.0 - math.cos(t * math.pi / 2)


# --- Image helpers ---

def gaussian_blur(arr: np.ndarray, radius: float) -> np.ndarray:
    if radius < 0.4:
        return arr
    blurred = Image.fromarray(arr.astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(radius=radius)
    )
    return np.array(blurred, dtype=np.float32)


def shift_y(arr: np.ndarray, ty: int, H: int) -> np.ndarray:
    """Return arr translated vertically by ty pixels (negative = up)."""
    if ty == 0:
        return arr
    out = np.zeros_like(arr)
    img_r0 = max(0,  -ty)
    img_r1 = min(H, H - ty)
    cvs_r0 = max(0,   ty)
    cvs_r1 = min(H, H + ty)
    rows = min(img_r1 - img_r0, cvs_r1 - cvs_r0)
    if rows > 0:
        out[cvs_r0:cvs_r0 + rows] = arr[img_r0:img_r0 + rows]
    return out


# --- Video writer ---

def open_ffmpeg(W: int, H: int, fps: int, output: str) -> subprocess.Popen:
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24",
        "-r", str(fps), "-i", "pipe:0",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "18", "-preset", "medium",
        output,
    ]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

def write_frame(proc: subprocess.Popen, arr: np.ndarray) -> None:
    proc.stdin.write(np.clip(arr, 0, 255).astype(np.uint8).tobytes())

def write_solid(proc: subprocess.Popen, arr: np.ndarray, n: int) -> None:
    data = np.clip(arr, 0, 255).astype(np.uint8).tobytes()
    for _ in range(n):
        proc.stdin.write(data)


# --- Main ---

def main():
    paths = [os.path.join(IMAGE_DIR, f"{i}.jpg") for i in range(1, 7)]
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        print(f"ERROR: missing files: {missing}", file=sys.stderr)
        sys.exit(1)

    print("Loading images...")
    raw = [Image.open(p).convert("RGB") for p in paths]
    W, H = raw[0].size
    W = W if W % 2 == 0 else W - 1   # yuv420p requires even dimensions
    H = H if H % 2 == 0 else H - 1
    arrays = [
        np.array(img.resize((W, H), Image.LANCZOS), dtype=np.float32)
        for img in raw
    ]
    N = len(arrays)
    print(f"  Canvas: {W}×{H}, {N} images")

    TF   = max(1, int(round(FADE_SEC  * FPS)))
    TM   = max(1, int(round(MORPH_SEC * FPS)))
    HOLD = max(1, int(round(HOLD_SEC  * FPS)))
    print(f"  fade={FADE_SEC}s ({TF}f)  morph={MORPH_SEC}s ({TM}f)  hold={HOLD_SEC}s ({HOLD}f)")
    print(f"  Total: ~{(TF + N*HOLD + (N-1)*TM + TF) / FPS:.1f}s at {FPS} fps")
    print(f"Writing → {OUTPUT}")

    proc = open_ffmpeg(W, H, FPS, OUTPUT)

    for i, arr in enumerate(arrays):
        label = f"  [{i+1}/{N}]"

        # ── Fade-in: first image only ──────────────────────────────────────
        if i == 0:
            print(f"{label} fade-in")
            for f in range(TF):
                t   = ease_out((f + 1) / TF)
                ty  = int(round(-Y_OFFSET * (1.0 - t)))
                blr = FADE_BLUR * (1.0 - t)
                frame = shift_y(arr, ty, H)
                frame = gaussian_blur(frame, blr) * t   # opacity = t
                write_frame(proc, frame)

        # ── Hold ───────────────────────────────────────────────────────────
        print(f"{label} hold ({HOLD_SEC}s)")
        write_solid(proc, arr, HOLD)

        # ── Blur-morph to next  /  fade-out on last ────────────────────────
        if i < N - 1:
            next_arr = arrays[i + 1]
            print(f"{label} → [{i+2}/{N}] blur-morph")
            for f in range(TM):
                t = (f + 1) / TM

                # Linear crossfade between the two images
                blend = arr * (1.0 - t) + next_arr * t

                # Sine-arch blur: 0 at both ends, peaks at t=0.5
                # sin(t·π) naturally produces this shape
                blur_r = MORPH_BLUR * math.sin(t * math.pi)

                write_frame(proc, gaussian_blur(blend, blur_r))
        else:
            print(f"{label} fade-out")
            for f in range(TF):
                t   = ease_in((f + 1) / TF)
                blr = FADE_BLUR * t
                frame = gaussian_blur(arr, blr) * (1.0 - t)  # opacity = 1-t
                write_frame(proc, frame)

    proc.stdin.close()
    proc.wait()

    if proc.returncode == 0:
        size_mb = os.path.getsize(OUTPUT) / 1_048_576
        print(f"\nDone! {OUTPUT} ({size_mb:.1f} MB)")
    else:
        print(f"\nERROR: ffmpeg exited with code {proc.returncode}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
