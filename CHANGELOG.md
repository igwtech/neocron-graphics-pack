# Changelog

All notable changes to this addon will be documented in this file.

## [0.2.1] — Unreleased

**Adds DirectX 9 support for Neocron Evolution.** The Evolution build
dropped DX8 and only renders through DX9, so the existing `D3D8.dll`
wrapper sat idle and ReShade never hooked the swapchain. v0.2.1 ships
`D3D9.dll` alongside `D3D8.dll` and overrides both — works for either
client variant without user intervention.

### Changed

- Fetch entry for dgVoodoo2 now extracts both `MS/x86/D3D8.dll` and
  `MS/x86/D3D9.dll` into the install dir.
- `wineDllOverrides`: `["d3d8", "d3d9", "dxgi"]` (was `["d3d8", "dxgi"]`).
- README clarifies that NC2 retail is DX8 and Evolution is DX9.

### Why

The in-game Display Settings dialog on Evolution only offers `(D3D9/0)`
as a renderer — there is no DX8 option. Without this fix, the addon
appears installed but produces no visible effect because the wrapper
DLL the game loads (`D3D9.dll`) doesn't exist.

## [0.2.0] — 2026-05-01

**Zero manual steps.** The two pieces that previously required hand-installing
(ReShade `dxgi.dll` and the crosire shader pack) are now auto-fetched by the
launcher alongside dgVoodoo2.

### Changed

- `addon.json` `fetch` now declares **three** upstream sources:
    1. dgVoodoo2 v2.87.1 zip → `D3D8.dll` (unchanged)
    2. ReShade 6.7.3 (`ReShade_Setup_6.7.3_Addon.exe`) → `ReShade32.dll`
       extracted with 7z and renamed to `dxgi.dll` (new)
    3. crosire/reshade-shaders nvidia branch tarball → `*.fx`/`*.fxh` routed
       into `reshade-shaders/Shaders/`, textures (`*.png`/`*.jpg`/`*.dds`/
       `*.tga`) routed into `reshade-shaders/Textures/` via glob (new)
- Removed `expects[]` — nothing is missing post-install anymore.
- Removed empty `reshade-shaders/` placeholder dir from the repo. Fetch
  creates the tree.

### Required launcher

This addon now requires a launcher with `extract: "exe"` and glob support
in `fetch.files.src`. Use the launcher release that ships those changes
(see launcher repo's release notes).

### Required tooling

`7z` must be on `PATH` for the ReShade .exe extraction. The README documents
install commands per-OS.

### Pinned upstream versions

- `D3D8.dll`: dgVoodoo2 **v2.87.1** (zip from `dgVoodoo2_87_1.zip` on the
  GitHub release).
- `dxgi.dll`: ReShade **6.7.3 with full add-on support** from
  `https://reshade.me/downloads/ReShade_Setup_6.7.3_Addon.exe`. Pinned —
  bump the URL in `addon.json` to track newer versions.
- shader pack: crosire/reshade-shaders **nvidia** branch tarball — only
  pack that ships SMAA + MXAO + Bloom + LevelsPlus + Vibrance +
  AdaptiveSharpen together.

## [0.1.0] — 2026-04-29

Initial release. Uses the Neocron Launcher's `fetch` manifest field to
auto-download dgVoodoo2 from upstream at install time; ReShade and the
shader pack remained manual one-time steps in this version.

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
