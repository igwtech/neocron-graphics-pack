#!/usr/bin/env python3
"""
Apply Neocron-tuned uniform defaults to ReShade .fx files in-place.
Mirrors what Windows ReShadePreset.ini does, but baked into the shader
defaults since vkBasalt 0.3.2.10 doesn't read ReShade preset files.
"""
import re
import sys
from pathlib import Path

SHADERS = Path.home() / "Neocron2" / "reshade-shaders" / "Shaders"

# Map of shader file -> [(uniform_name, new_default_expr)]
TUNINGS = {
    "Bloom.fx": [
        ("iBloomMixmode",       "2"),
        # Bloom amount and saturation backed off — they were producing
        # red feedback spill: bloom-saturated neon → SSIL bounces it →
        # Vibrance amplifies → LUT push. Saturation 1.0 = neutral
        # (bloom keeps source color, doesn't amplify). Amount 0.85 means
        # less neon bleed onto walls.
        ("fBloomThreshold",     "0.65"),
        ("fBloomAmount",        "0.85"),
        ("fBloomSaturation",    "1.00"),
        ("fBloomTint",          "float3(0.55, 0.70, 1.00)"),
        ("bLensdirtEnable",     "false"),
    ],
    "MXAO.fx": [
        # Kept for reference but no longer used in the chain — replaced
        # by qUINT_mxao which adds SSIL for object grounding.
        ("MXAO_GLOBAL_SAMPLE_QUALITY_PRESET", "2"),
        ("MXAO_SAMPLE_RADIUS",                "2.50"),
        ("MXAO_SAMPLE_NORMAL_BIAS",           "0.20"),
        ("MXAO_GLOBAL_RENDER_SCALE",          "0.50"),
        ("MXAO_SSAO_AMOUNT",                  "1.10"),
        ("MXAO_GAMMA",                        "1.50"),
        ("MXAO_BLEND_TYPE",                   "0"),
    ],
    "qUINT_mxao.fx": [
        # 1.80 was eating ambient ALL the way to black on unlit walls.
        # 1.30 still gives clearly visible object grounding + corner
        # shading without absorbing diffuse light entirely.
        ("MXAO_SSAO_AMOUNT", "1.30"),
        # SSIL = Screen-Space Indirect Lighting. Adds the bounced-light
        # darkening that makes boxes/tires look grounded.
        ("MXAO_SSIL_AMOUNT", "4.00"),
        # Saturation lowered: 1.30 was bouncing fully-saturated neon onto
        # neighboring walls, which combined with Bloom + Vibrance to paint
        # entire scenes one colour. 0.80 means bounced light is desaturated
        # — still picks up tint, doesn't dominate.
        ("MXAO_SSIL_SATURATION", "0.80"),
        # Wider sample radius = AO/SSIL felt at larger scale, gives
        # better grounding on bigger objects (vehicles, pillars).
        ("MXAO_SAMPLE_RADIUS", "3.00"),
        # Multiply blend (0) darkens corners more aggressively than the
        # subtract blend (1). Default is multiply but we set explicitly.
        ("MXAO_BLEND_TYPE", "0"),
    ],
    "PPFX_SSDO.fx": [
        # Mid-strength SSDO (2.50/2.00 was too aggressive, default
        # 1.5/1.5 invisible). 1.90/1.70 visible BSP edges without
        # killing playability.
        ("pSSDOIntensity", "1.90"),
        ("pSSDOAmount", "1.70"),
        # Smaller sample range catches tighter corners.
        ("pSSDOSampleRange", "50.0"),
        ("pSSDOAngleThreshold", "0.200"),
    ],
    "LevelsPlus.fx": [
        # No black crush — letting near-black pixels survive lets gamma
        # lift them. The earlier 10/255 crush meant anything below that
        # got clipped to 0 BEFORE gamma was applied, and gamma can't
        # rescue 0.
        ("InputBlackPoint",  "float3(0/255.0f, 0/255.0f, 0/255.0f)"),
        ("InputWhitePoint",  "float3(245/255.0f, 245/255.0f, 245/255.0f)"),
        # Gamma 0.40 (= display-gamma 2.5 equivalent) — strong midtone
        # lift to compensate for the AO stack. ReShade's gamma is raw
        # pow(input, gamma), not the inverse, so gamma<1 brightens.
        ("InputGamma",       "float3(0.40f, 0.40f, 0.40f)"),
        ("OutputBlackPoint", "float3(0/255.0f, 0/255.0f, 0/255.0f)"),
        ("OutputWhitePoint", "float3(255/255.0f, 255/255.0f, 255/255.0f)"),
    ],
    "Vibrance.fx": [
        # Halved again from 0.20 — already-saturated neons don't need
        # extra push from Vibrance when Bloom + SSIL are providing color
        # bleed. 0.10 is a final gentle nudge, not a primary effect.
        ("Vibrance",            "0.10"),
        ("VibranceRGBBalance",  "float3(1.0, 1.0, 1.0)"),
        ("Vibrance_Luma",       "1"),
    ],
    "qUINT_ssr.fx": [
        # Tuned in two passes: first pass at 0.40 was invisible in normal
        # play (only visible on the brightest neon), second pass bumps it
        # to 0.70 — clearly readable wet-floor effect on Pepper Park asphalt
        # without turning matte walls into mirrors. Fade slightly raised
        # too (reflections used to clip too aggressively at mid-range).
        ("SSR_REFLECTION_INTENSITY", "0.70"),
        ("SSR_FADE_DIST",            "0.60"),
        # Lower fresnel exp = more reflections off non-glancing angles.
        # Neocron geometry has no PBR roughness signal, so without
        # softening fresnel only steep-angle surfaces reflect. 2.5 gives
        # noticeable reflections on near-flat floors too.
        ("SSR_FRESNEL_EXP",          "2.5"),
        # Relief simulates surface micro-detail (wet pavement texture)
        # so reflections look like real wet floor instead of a chrome
        # mirror. 0.12 is enough to break up perfect reflection without
        # losing the effect.
        ("SSR_RELIEF_AMOUNT",        "0.12"),
    ],
    "AdaptiveSharpen.fx": [
        ("curve_height",   "1.00"),
        ("curveslope",     "0.50"),
        ("L_overshoot",    "0.003"),
        ("L_compr_low",    "0.169"),
        ("L_compr_high",   "0.337"),
        ("D_overshoot",    "0.009"),
        ("D_compr_low",    "0.253"),
        ("D_compr_high",   "0.504"),
    ],
}

# Match `uniform <type> <name>` declaration, then capture everything up to the
# first `= <something>;` after a closing `>`. The default value is on the line
# that starts with `>` and ends with `= ...;`.
def patch_default(text: str, uniform: str, new_default: str) -> tuple[str, bool]:
    # The metadata block contains semicolons (`ui_min = X; ui_max = Y;`),
    # so we have to match up to the first line that starts with `>`.
    # MULTILINE lets `^>` anchor to start-of-line; DOTALL lets `.*?` cross
    # newlines while staying minimal.
    pattern = re.compile(
        r"(uniform\s+\w+\s+" + re.escape(uniform) + r"\b.*?^>\s*=\s*)([^;]+)(;)",
        re.DOTALL | re.MULTILINE,
    )
    new_text, n = pattern.subn(rf"\g<1>{new_default}\g<3>", text, count=1)
    return new_text, n == 1


def main():
    for fname, tunings in TUNINGS.items():
        path = SHADERS / fname
        if not path.exists():
            print(f"[skip] {path} does not exist")
            continue
        # Backup once
        bak = path.with_suffix(path.suffix + ".orig")
        if not bak.exists():
            bak.write_text(path.read_text())
        text = bak.read_text()  # always re-apply from pristine backup
        for uname, val in tunings:
            text, ok = patch_default(text, uname, val)
            print(f"  {'OK ' if ok else '?? '} {fname}::{uname} = {val}")
        path.write_text(text)
    print("done")

if __name__ == "__main__":
    main()
