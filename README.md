# Neocron Graphics Pack — dgVoodoo2 + ReShade

Modernizes the Neocron 2 renderer. Installs through the
[Neocron Launcher](https://github.com/igwtech/Neocron-Launcher) addon system —
no manual file copying, no broken layered overrides, no clobbering on game
patch.

```
Game DirectX 8 calls
  -> dgVoodoo2 D3D8.dll      (translates DX8 to D3D11)
    -> ReShade dxgi.dll       (hooks the D3D11 swapchain, runs shaders)
      -> Wine/Proton DXGI -> Vulkan (DXVK) on Linux/macOS, native D3D11 on Windows
```

## Why this stack

ReShade dropped DirectX 8 support, so it can't hook Neocron directly. dgVoodoo2
promotes the DX8/DX9 calls to D3D11, which ReShade *can* hook through `dxgi.dll`.
This is the standard recipe for modernizing early-2000s games.

The original Neocron 2 client uses **DirectX 8**; **Neocron Evolution** dropped
DX8 and only renders through **DirectX 9**. The addon ships both `D3D8.dll` and
`D3D9.dll` wrappers and overrides both, so it works regardless of which client
is selected in the in-game Display Settings dialog.

You get:
- D3D11/12 backend with anisotropic filtering, MSAA, integer scaling
- Modern post-processing: SMAA/FXAA, tonemapping, lumasharpen, bloom, depth-of-field
- Optional shader effects you can toggle in-game with the ReShade overlay

## Installing in the launcher

1. Open the launcher → **Addons** tab.
2. Paste `https://github.com/igwtech/neocron-graphics-pack` → **Install**.
3. Launch the game.

That's it. The launcher auto-fetches all three upstream pieces (dgVoodoo2,
ReShade, the shader pack) from their official sources and stamps them into
the install dir alongside the configs from this repo. It also composes
`WINEDLLOVERRIDES=quartz=n,b;d3d8=n,b;d3d9=n,b;dxgi=n,b` for you — no Proton
tweaking required.

> **Dependency**: the launcher needs `7z` on `PATH` to unpack the ReShade
> installer (a .NET self-extractor — Go's stdlib doesn't read its format).
> - **Linux**: `pacman -S p7zip` / `apt install p7zip-full` / `dnf install p7zip`
> - **macOS**: `brew install p7zip`
> - **Windows**: install [7-Zip](https://www.7-zip.org/) and ensure it's on `PATH`

## What's bundled vs auto-fetched

| Component | Source | How |
|---|---|---|
| `dgVoodoo.conf`, `ReShade.ini`, `ReShadePreset.ini` | this repo | Bundled — copied straight in |
| `D3D8.dll` + `D3D9.dll` (dgVoodoo2 v2.87.1, MS/x86) | <https://github.com/dege-diosg/dgVoodoo2/releases> | **Auto-fetched** at install |
| `dxgi.dll` (ReShade 6.7.3, 32-bit) | <https://reshade.me/downloads/ReShade_Setup_6.7.3_Addon.exe> | **Auto-fetched** at install (extracted with 7z) |
| `reshade-shaders/Shaders/` + `Textures/` (curated pack) | <https://github.com/crosire/reshade-shaders> (nvidia branch) | **Auto-fetched** at install |

ReShade's authors prefer that binaries not be redistributed — every user
should pull fresh from the official site. Auto-fetch respects that: the
files come from upstream URLs to the user's machine at install time, never
mirrored or hosted by this repo.

## Forking and customizing

If you want to publish your own variant (different shader presets, different
dgVoodoo settings):

1. Fork or clone:
   ```bash
   git clone https://github.com/igwtech/neocron-graphics-pack.git
   cd neocron-graphics-pack
   ```
2. Edit `dgVoodoo.conf` and/or `ReShadePreset.ini` to taste.
3. Update `addon.json`'s `id` (must be unique) and `version`.
4. Push to your fork. Users install via the fork's URL.

The auto-fetch URL in `addon.json` can also be retargeted — pin a different
dgVoodoo2 release, or reference an internal mirror.

## How the launcher integrates

When this addon is enabled:

| Mechanism | What happens |
|---|---|
| **Repo files** | `dgVoodoo.conf`, `ReShade.ini`, and `ReShadePreset.ini` are stamped from this repo into the game install dir. |
| **Auto-fetch** | Three `fetch` entries in `addon.json` pull dgVoodoo2 (zip → `D3D8.dll`), ReShade (.exe extracted with 7z → `dxgi.dll`), and the shader pack (tar.gz → glob-routed into `Shaders/` + `Textures/`). All from upstream URLs, never mirrored by this repo. |
| **Wine DLL overrides** | `wineDllOverrides: ["d3d8", "d3d9", "dxgi"]` adds `d3d8=n,b;d3d9=n,b;dxgi=n,b` to `WINEDLLOVERRIDES`. Native-then-builtin makes Wine prefer the dropped-in DLLs. |
| **Pristine pool** | Original game files are snapshotted before being overwritten. Disabling restores them — even with other addons stamping the same paths, the launcher's stacked-restore handles layering. |
| **CDN-update safety** | When the launcher patches the game, it un-stamps addons first, lets the updater run on pristine, refreshes the pristine pool, then re-stamps. Wrapper DLLs survive game patches. |

You don't need to think about any of this. Install once, play.

## Compatibility notes

- **Resolution scaling**: leave dgVoodoo2 at 1× resolution. Neocron's UI is
  hard-coded for the screen mode set in-game.
- **MSAA + ReShade**: depth-buffer-aware shaders (DoF, SSAO) struggle when
  MSAA is on. Either drop MSAA to 1× or skip those shaders.
- **Anti-cheat**: not a concern — community servers (Ceres-J, TinNS) don't
  run client-side anti-cheat.
- **Linux/Proton**: `WINEDLLOVERRIDES` handles the DLL search order; DXVK
  picks up D3D11 calls from dgVoodoo2 transparently.
- **Native Windows**: the launcher applies the same drop-ins; no Wine env
  needed.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Game starts but no ReShade overlay | `dxgi.dll` not staged — check launcher's `addon.log` for fetch errors; ensure `7z` is on `PATH` |
| Black screen | dgVoodoo `D3D8.dll` missing or x64 built (the auto-fetch picks x86) |
| ReShade shaders missing | `reshade-shaders/Shaders/` empty — check `addon.log`; the GitHub tarball fetch may have been blocked |
| Game patch broke wrapper | Re-launch the launcher; the post-update hook re-stamps automatically |
| HUD misaligned | dgVoodoo resolution forced — set `Resolution = unforced` in `dgVoodoo.conf` |

Logs to check (Linux):
- `~/.local/share/neocron-launcher/addons/addon.log` — addon manager
- `~/.local/share/neocron-launcher/prefix/pfx/drive_c/users/...` — Wine path
- `~/Neocron2/logs/error_*.log` — game's own log

## Licenses

- This repo's code, configs, docs: **MIT** (see `LICENSE`)
- `D3D8.dll` (dgVoodoo2): **freeware**, redistribution allowed under the
  dgVoodoo2 license. Auto-fetched at install time from upstream — never
  redistributed by this repo. Attribution: Dege.
- `dxgi.dll` (ReShade): **BSD 3-Clause**, but upstream asks redistributors
  not to bundle. We don't bundle — auto-fetched from <https://reshade.me>
  to the user's machine at install time. Attribution: Patrick Mours.
- `reshade-shaders/`: per upstream — typically MIT/BSD per shader. Auto-
  fetched from <https://github.com/crosire/reshade-shaders> at install
  time, never redistributed by this repo.
