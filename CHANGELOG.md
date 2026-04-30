# Changelog

All notable changes to this addon will be documented in this file.

## [0.1.0] — Unreleased

Initial release. Uses the Neocron Launcher's `fetch` manifest field to
auto-download dgVoodoo2 from upstream at install time; ReShade and the
shader pack remain manual one-time steps per upstream's redistribution
preferences.

- `addon.json` with `fetch` entry pointing at
  [dgVoodoo2 v2.87.1](https://github.com/dege-diosg/dgVoodoo2/releases/tag/v2.87.1)
  (`MS/x86/D3D8.dll`).
- `wineDllOverrides`: `["d3d8", "dxgi"]` — composed into `WINEDLLOVERRIDES`
  by the launcher.
- `dgVoodoo.conf` preconfigured for Neocron 2 (best D3D11 backend, 8× MSAA,
  16× AF, vsync on, resolution unforced to preserve hard-coded HUD layout).
- `ReShade.ini` minimal config pointing at `./reshade-shaders/Shaders` and
  `./reshade-shaders/Textures`.
- `ReShadePreset.ini` with a Neocron-tuned cyberpunk pipeline:
    - **SMAA** — kills edge crawl on stair-stepped geometry
    - **MXAO** — adds the contact shadows the original engine never had
    - **Bloom** (cyan-tinted) — makes the city's neon signs and HUD light glow
    - **LevelsPlus** — crushes blacks (18/255) for that filmic deep-shadow look
    - **Vibrance** — boosts neon saturation without flattening skin tones
    - **AdaptiveSharpen** — recovers texture detail buried under bilinear filtering

### Pinned upstream versions

- `D3D8.dll`: dgVoodoo2 **v2.87.1** (released 2026-04-07) —
  fetched from `dgVoodoo2_87_1.zip` at the GitHub release. Update the
  `fetch.from` URL in `addon.json` to track newer releases.
- `dxgi.dll`: ReShade — **manual install** from <https://reshade.me>.
  No version pinned; users get current.
- shader pack: crosire/reshade-shaders **nvidia** branch — manual clone.
  This is the only mainstream pack that ships all six default-preset
  techniques (SMAA + MXAO + Bloom + LevelsPlus + Vibrance + AdaptiveSharpen).
  The slim branch ships only 5 shaders (none matching this preset);
  legacy ships ~20 but lacks SMAA and MXAO.
