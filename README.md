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
promotes the DX8 calls to D3D11, which ReShade *can* hook through `dxgi.dll`.
This is the standard recipe for modernizing early-2000s games.

You get:
- D3D11/12 backend with anisotropic filtering, MSAA, integer scaling
- Modern post-processing: SMAA/FXAA, tonemapping, lumasharpen, bloom, depth-of-field
- Optional shader effects you can toggle in-game with the ReShade overlay

## Installing in the launcher

1. Open the launcher → **Addons** tab.
2. Paste `https://github.com/igwtech/neocron-graphics-pack` → **Install**.
3. The launcher auto-fetches dgVoodoo2 from its GitHub release; configs and
   shader directory structure ship with this repo.
4. The addon card will show a pulsing **"3 file(s) missing"** badge — that's
   the launcher reporting which manual steps still need doing. Hover for the
   list. Complete them (see "Manual steps" below) and the badge disappears
   on next refresh.
5. Launch the game.

The launcher composes `WINEDLLOVERRIDES=quartz=n,b;d3d8=n,b;dxgi=n,b`
automatically; no Proton tweaking required.

## What's bundled vs auto-fetched vs manual

| Component | Source | How |
|---|---|---|
| `dgVoodoo.conf`, `ReShade.ini`, `ReShadePreset.ini` | this repo | Bundled — copied straight in |
| `D3D8.dll` (dgVoodoo2 v2.87.1, MS/x86) | <https://github.com/dege-diosg/dgVoodoo2/releases> | **Auto-fetched** by launcher on install |
| `dxgi.dll` (ReShade) | <https://reshade.me> | **Manual** (see below) |
| `reshade-shaders/` (curated shader pack) | <https://github.com/crosire/reshade-shaders> | **Manual** (see below) |

## Manual steps (one-time)

ReShade's authors explicitly ask people not to redistribute the binaries or
shader files — they want every user to download fresh from the official site.
We respect that. Here's the minimal-friction path:

### 1. ReShade dxgi.dll

1. Download "ReShade with full add-on support" from <https://reshade.me>.
2. Run the installer against any throwaway D3D11 EXE (e.g. `notepad++.exe`).
   Pick "DirectX 10/11/12" when asked.
3. The installer drops `dxgi.dll` next to the throwaway EXE. Copy that file
   into your Neocron install root (next to `neocronclient.exe`).

### 2. Shader pack

```bash
git clone -b slim --depth 1 https://github.com/crosire/reshade-shaders \
  /tmp/reshade-shaders
cp -r /tmp/reshade-shaders/Shaders /tmp/reshade-shaders/Textures \
  ~/Neocron2/reshade-shaders/
```

(Adjust `~/Neocron2/` to your install dir.)

### 3. Verify

```bash
cd ~/Neocron2  # your Neocron install dir
test -f D3D8.dll && test -f dxgi.dll && \
  test -d reshade-shaders/Shaders && echo "Layout OK" || echo "Missing files"
```

`D3D8.dll` is staged automatically by the launcher; the other two are what
the manual steps add.

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
| **Repo files** | `dgVoodoo.conf`, `ReShade.ini`, `ReShadePreset.ini`, and `reshade-shaders/` directory tree are stamped from this repo into the game install dir. |
| **Auto-fetch** | The `fetch` field in `addon.json` triggers download of the dgVoodoo2 release zip, extraction, and staging of `MS/x86/D3D8.dll` — without us redistributing the file. |
| **Wine DLL overrides** | `wineDllOverrides: ["d3d8", "dxgi"]` adds `d3d8=n,b;dxgi=n,b` to `WINEDLLOVERRIDES`. Native-then-builtin makes Wine prefer the dropped-in DLLs. |
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
| Game starts but no ReShade overlay | `dxgi.dll` not in install dir — rerun manual step 1 |
| Black screen | dgVoodoo `D3D8.dll` missing or x64 built (the auto-fetch picks x86) |
| ReShade shaders missing | `reshade-shaders/Shaders/` empty — rerun manual step 2 |
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
  not to bundle. We don't bundle. Manual install. Attribution: Patrick Mours.
- `reshade-shaders/`: per upstream — typically MIT/BSD per shader. Cloned
  fresh by the user per upstream's preference.
