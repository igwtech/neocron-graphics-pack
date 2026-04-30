# Changelog

All notable changes to this addon will be documented in this file.

## [0.1.0] — Unreleased

Initial scaffolding. Pre-publish — binaries not yet bundled.

- `addon.json` declaring the dgVoodoo2 + ReShade file map and Wine DLL
  overrides for `d3d8` and `dxgi`.
- `dgVoodoo.conf` preconfigured for Neocron 2 (best D3D11 backend, 8× MSAA,
  16× AF, vsync on, resolution unforced to preserve hard-coded HUD layout).
- `ReShade.ini` minimal preset pointing at the bundled shader paths.
- `ReShadePreset.ini` with LumaSharpen + SMAA + AmbientLight enabled by
  default — sane upgrades that don't change the game's look drastically.

To publish: drop in `D3D8.dll` (dgVoodoo2 MS/x86), `dxgi.dll` (ReShade),
populate `reshade-shaders/Shaders/` and `reshade-shaders/Textures/` with the
[crosire/reshade-shaders](https://github.com/crosire/reshade-shaders) slim
branch, then `git tag v0.1.0 && git push --tags`.

### Binary versions to pin

When you bundle the binaries, record the upstream versions + SHA-256 hashes
here so users can audit what they're getting:

- `D3D8.dll`: dgVoodoo2 v____ — `sha256: ____`
- `dxgi.dll`: ReShade v____ — `sha256: ____`
- shader pack: crosire/reshade-shaders @ commit `____`
