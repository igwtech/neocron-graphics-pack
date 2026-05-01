# Vendored shader attribution

The Linux/macOS path of this addon ships **modified versions** of seven
ReShade `.fx` shader files in `reshade-shaders/Shaders/`. The
modifications are limited to changing the default values of `uniform`
declarations to match the cyberpunk preset we ship for Windows. No
shader logic, technique definitions, or copyright notices were altered.

The originals come from two upstream projects, both redistribution-
permissive. We mirror only the seven files we tuned; everything else
in `reshade-shaders/` is auto-fetched from upstream at install time.

| Vendored file | Upstream | Author | License |
|---|---|---|---|
| `Bloom.fx` | <https://github.com/crosire/reshade-shaders/tree/nvidia> | crosire et al. | MIT |
| `LevelsPlus.fx` | <https://github.com/crosire/reshade-shaders/tree/nvidia> | crosire et al. | MIT |
| `Vibrance.fx` | <https://github.com/crosire/reshade-shaders/tree/nvidia> | crosire et al. | MIT |
| `AdaptiveSharpen.fx` | <https://github.com/crosire/reshade-shaders/tree/nvidia> | crosire et al. | MIT |
| `PPFX_SSDO.fx` | <https://github.com/crosire/reshade-shaders/tree/nvidia> | euda / crosire et al. | MIT |
| `qUINT_mxao.fx` | <https://github.com/martymcmodding/qUINT> | Marty McFly | MIT (see qUINT repo) |
| `qUINT_ssr.fx` | <https://github.com/martymcmodding/qUINT> | Marty McFly | MIT (see qUINT repo) |

## What we changed

Per-uniform default values only — see `tools/tune_shaders.py` for the
full list of changes applied to fresh upstream copies. The script is
idempotent and keeps `.fx.orig` backups, so a user with vanilla
upstream copies can reproduce our shipped versions exactly by running:

```bash
python3 tools/tune_shaders.py
```

## Re-syncing with upstream

If upstream ships a major shader update we want to absorb:

1. Fetch fresh copies of the seven files into `reshade-shaders/Shaders/`.
2. Run `python3 tools/tune_shaders.py` to re-apply our defaults.
3. Manually inspect each `.fx` for any new uniform our recipe doesn't
   touch — bake those if needed.

## Why ship modified `.fx` files at all?

vkBasalt 0.3.2.10 doesn't read `ReShadePreset.ini`. The only way to
ship per-uniform tuning that survives re-fetch is to override the
`.fx` defaults at the shader-source level. The launcher's
"stamp-files-after-fetch" ordering (Neocron-Launcher v0.4+) makes
the override automatic: the addon fetches upstream first, then our
seven files override the affected `.fx` defaults.

## Cyberpunk LUT

`reshade-shaders/Textures/neocron_cyberpunk_lut.png` is a 1024×32
ReShade-format LUT generated procedurally by `tools/build_lut.py`
(MIT, Neocron Community). It is not vendored — the recipe is in the
repo and any user can regenerate or replace it.
