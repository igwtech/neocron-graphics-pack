#!/usr/bin/env python3
"""
Build a cyberpunk-grading 3D LUT image for vkBasalt's `lut` effect.

The standard ReShade LUT format is a horizontal strip of 32 squares,
each 32x32, encoding a 32^3 RGB cube. Pixel (x, y) in square N stores
the output colour for input (x/31, y/31, N/31).

Cyberpunk grading recipe:
- Lift shadows toward cyan-blue (cool ambient light)
- Push highlights toward magenta-pink (neon spill)
- Slight crush in midtone-blacks for filmic depth
- Boost saturation in already-saturated colours (vibrance-style)
- Avoid clipping skin tones
"""
import numpy as np
from PIL import Image
from pathlib import Path

SIZE = 32           # cube size — ReShade convention
OUT = Path.home() / "Neocron2" / "reshade-shaders" / "Textures" / "neocron_cyberpunk_lut.png"


def cube_indices():
    # Returns three (SIZE, SIZE, SIZE) arrays with R, G, B normalised
    # input coordinates in [0,1].
    r = np.linspace(0, 1, SIZE)[None, None, :]
    g = np.linspace(0, 1, SIZE)[None, :, None]
    b = np.linspace(0, 1, SIZE)[:, None, None]
    R, G, B = np.broadcast_arrays(r, g, b)
    return R.copy(), G.copy(), B.copy()


def smoothstep(x, lo=0.0, hi=1.0):
    t = np.clip((x - lo) / (hi - lo), 0, 1)
    return t * t * (3 - 2 * t)


def cyberpunk(R, G, B):
    # Shadows mask: weight = how dark the pixel is.
    luma = 0.2126 * R + 0.7152 * G + 0.0722 * B
    shadow_mask = 1.0 - smoothstep(luma, 0.0, 0.45)      # 1 in shadows, 0 in mids+
    highlight_mask = smoothstep(luma, 0.55, 1.0)         # 0 in mids-, 1 in highlights

    # Cyan-blue tint in shadows — halved from first pass. Vibrance + the
    # game's existing green-heavy UI elements amplified the lift enough
    # to wash 2D screens (login) olive-green; this tones it down.
    shadow_tint_r = -0.02
    shadow_tint_g = +0.01
    shadow_tint_b = +0.03

    # Magenta-pink tint in highlights — also halved.
    highlight_tint_r = +0.025
    highlight_tint_g = -0.01
    highlight_tint_b = +0.02

    R2 = R + shadow_mask * shadow_tint_r + highlight_mask * highlight_tint_r
    G2 = G + shadow_mask * shadow_tint_g + highlight_mask * highlight_tint_g
    B2 = B + shadow_mask * shadow_tint_b + highlight_mask * highlight_tint_b

    # Slight black crush — only the very darkest pixels, not enough to hurt
    # readability of HUD text or chat overlays.
    crush = 1.0 - smoothstep(luma, 0.0, 0.10)
    R2 = R2 - 0.04 * crush
    G2 = G2 - 0.04 * crush
    B2 = B2 - 0.03 * crush

    # Vibrance: amplify saturation in pixels that already have some, leave
    # near-greys alone (preserves skin tones).
    luma2 = 0.2126 * R2 + 0.7152 * G2 + 0.0722 * B2
    sat = np.maximum.reduce([R2, G2, B2]) - np.minimum.reduce([R2, G2, B2])
    vib = 0.10 * (1.0 - sat)  # halved — Vibrance.fx already does saturation lift
    R2 = luma2 + (R2 - luma2) * (1 + vib)
    G2 = luma2 + (G2 - luma2) * (1 + vib)
    B2 = luma2 + (B2 - luma2) * (1 + vib)

    return np.clip(R2, 0, 1), np.clip(G2, 0, 1), np.clip(B2, 0, 1)


def main():
    R, G, B = cube_indices()
    R2, G2, B2 = cyberpunk(R, G, B)

    # Layout: horizontal strip of SIZE squares; square N is the slice
    # corresponding to B = N / (SIZE-1). Each square is SIZE×SIZE.
    img = np.zeros((SIZE, SIZE * SIZE, 3), dtype=np.uint8)
    for n in range(SIZE):
        x0 = n * SIZE
        img[:, x0:x0 + SIZE, 0] = (R2[n] * 255).astype(np.uint8)
        img[:, x0:x0 + SIZE, 1] = (G2[n] * 255).astype(np.uint8)
        img[:, x0:x0 + SIZE, 2] = (B2[n] * 255).astype(np.uint8)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(img).save(OUT)
    print(f"wrote {OUT} ({img.shape[1]}×{img.shape[0]})")


if __name__ == "__main__":
    main()
