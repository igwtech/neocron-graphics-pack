# Neocron Graphics Pack — dgVoodoo2 + ReShade / vkBasalt

Modernizes the Neocron 2 renderer. Installs through the
[Neocron Launcher](https://github.com/igwtech/Neocron-Launcher) addon system —
no manual file copying, no broken layered overrides, no clobbering on game
patch.

The addon takes a **different path per platform**, because the obvious
"dgVoodoo2 + ReShade everywhere" approach breaks under Wine/Proton:

| Platform | Approach |
|---|---|
| **Windows native** | `dgVoodoo2` (DX8/DX9 → D3D11) + `ReShade` (hooks D3D11 swapchain) + curated shader pack |
| **Linux / macOS (Wine/Proton)** | `vkBasalt` Vulkan post-processing layer (built-in CAS sharpening) |

Why two paths? dgVoodoo2's D3D9 wrapper internally calls D3D11, and that
chain hits a known DXVK incompatibility — verified live with v0.2.1, the
game crashes with exit code 5 in a "Init D3D object → Shutdown driver"
loop. vkBasalt sidesteps the issue entirely by hooking at the Vulkan
layer, after DXVK has already done D3D9→Vulkan translation.

## Installing in the launcher

1. Open the launcher → **Addons** tab.
2. Paste `https://github.com/igwtech/neocron-graphics-pack` → **Install**.
3. Launch the game.

That's it — the launcher detects your platform and stamps the right files,
fetches the right upstream binaries, and sets the right environment
variables. You don't pick a "Linux" or "Windows" variant manually.

## Platform requirements

### Linux / macOS (vkBasalt path)

The launcher needs `vkbasalt` and its 32-bit companion library on PATH:

| Distro | Command |
|---|---|
| **Arch / Manjaro** | `yay -S vkbasalt lib32-vkbasalt` |
| **Debian / Ubuntu** | `apt install vkbasalt vkbasalt:i386` (after `dpkg --add-architecture i386`) |
| **Fedora** | `dnf install vkbasalt vkbasalt.i686` |
| **macOS (Whisky / CrossOver)** | build from <https://github.com/DadSchoorse/vkBasalt> |

The 32-bit variant is required because Neocron is a 32-bit Wine app and
DXVK loads same-bitness Vulkan layers.

### Windows native (dgVoodoo2 + ReShade path)

The launcher needs `7z` on `PATH` to unpack the ReShade installer (a .NET
self-extractor — Go's stdlib doesn't read its format).
Install [7-Zip](https://www.7-zip.org/) and ensure it's on `PATH`.

## What's auto-fetched per platform

| Component | Platforms | Source |
|---|---|---|
| `dgVoodoo.conf`, `ReShade.ini`, `ReShadePreset.ini` | Windows | bundled in this repo |
| `vkBasalt.conf` | Linux, macOS | bundled in this repo |
| `D3D8.dll` + `D3D9.dll` (dgVoodoo2 v2.87.1, MS/x86) | Windows | <https://github.com/dege-diosg/dgVoodoo2/releases> |
| `dxgi.dll` (ReShade 6.7.3, 32-bit) | Windows | <https://reshade.me/downloads/ReShade_Setup_6.7.3_Addon.exe> |
| `reshade-shaders/Shaders/` + `Textures/` | Windows | <https://github.com/crosire/reshade-shaders> (nvidia branch) |

ReShade's authors prefer that binaries not be redistributed — every user
should pull fresh from the official site. Auto-fetch respects that: the
files come from upstream URLs to the user's machine at install time, never
mirrored or hosted by this repo.

## Effects shipped

### Windows (ReShade preset)

`SMAA` + `MXAO` + `Bloom` (cyan-tinted) + `LevelsPlus` (crushed blacks) +
`Vibrance` + `AdaptiveSharpen`. Press **Home** in-game to open the ReShade
overlay and tweak. See `ReShadePreset.ini` for tuning notes.

### Linux / macOS (vkBasalt config)

`CAS` only — Contrast Adaptive Sharpening, recovers texture detail
buried under DXVK's bilinear filtering. Press **Home** to toggle
on/off. See `vkBasalt.conf` for tuning.

> **Why no SMAA?** Both `effects = smaa,cas` and `effects = fxaa,cas`
> were tested live and crash Neocron Evolution during D3D9 init under
> DXVK 2.x + vkBasalt 0.3.2.10 + Proton GE-9-26. vkBasalt's
> anti-aliasing implementations don't tolerate Neocron's swapchain
> format. CAS-only launches cleanly. We'll revisit SMAA when upstream
> vkBasalt fixes the AA crash.

The Linux/macOS preset is intentionally minimal — built-in effects
only, no external `.fx` shader files. A future version may add
Bloom/LevelsPlus/Vibrance via vkBasalt's ReShade `.fx` loader to
match the Windows preset's cyberpunk colour grading.

## How the launcher integrates

When this addon is enabled:

| Mechanism | What happens |
|---|---|
| **Repo files (platform-gated)** | Only the configs matching `runtime.GOOS` are stamped — `vkBasalt.conf` on Linux/macOS, dgVoodoo + ReShade configs on Windows. |
| **Auto-fetch (platform-gated)** | dgVoodoo2 / ReShade / shader pack only fetch on Windows. The Linux path fetches nothing — vkBasalt is a system package. |
| **Wine DLL overrides** | `wineDllOverrides: ["d3d8", "d3d9", "dxgi"]` adds `d3d8=n,b;d3d9=n,b;dxgi=n,b` to `WINEDLLOVERRIDES`. On Linux those are inert (no native DLLs staged); on Windows they make Wine prefer the dropped-in DLLs. |
| **Env vars (platform-gated)** | On Linux/macOS, sets `ENABLE_VKBASALT=1` and `VKBASALT_CONFIG_FILE=<install_dir>/vkBasalt.conf` — activates the Vulkan layer for this launch only. |
| **Pristine pool** | Original game files are snapshotted before being overwritten. Disabling restores them — even with other addons stamping the same paths, the launcher's stacked-restore handles layering. |
| **CDN-update safety** | When the launcher patches the game, it un-stamps addons first, lets the updater run on pristine, refreshes the pristine pool, then re-stamps. Wrapper DLLs and configs survive game patches. |

You don't need to think about any of this. Install once, play.

## Forking and customizing

If you want to publish your own variant (different shader presets,
different dgVoodoo settings, different vkBasalt effects):

1. Fork or clone:
   ```bash
   git clone https://github.com/igwtech/neocron-graphics-pack.git
   cd neocron-graphics-pack
   ```
2. Edit `dgVoodoo.conf`, `ReShadePreset.ini`, and/or `vkBasalt.conf` to taste.
3. Update `addon.json`'s `id` (must be unique) and `version`.
4. Push to your fork. Users install via the fork's URL.

The auto-fetch URLs in `addon.json` can also be retargeted — pin a
different dgVoodoo2 release, reference an internal mirror, or point at a
different ReShade shader pack.

## Compatibility notes

- **Resolution scaling**: leave dgVoodoo2 at 1× resolution. Neocron's UI
  is hard-coded for the screen mode set in-game.
- **MSAA + ReShade** (Windows): depth-buffer-aware shaders (DoF, SSAO)
  struggle when MSAA is on. Either drop MSAA to 1× or skip those shaders.
- **Anti-cheat**: not a concern — community servers (Ceres-J, TinNS)
  don't run client-side anti-cheat.
- **Linux/Proton**: vkBasalt activates as a Vulkan layer for the game
  process only — does not affect other apps.
- **Native Windows**: the launcher applies the same drop-ins; no Wine
  env needed.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| **Linux**: no visible change after enabling | `vkbasalt` / `lib32-vkbasalt` not installed, or `ENABLE_VKBASALT` env not set — check launcher's `addon.log` for env-var dump |
| **Linux**: game crashes immediately on launch | `D3D9.dll` got staged on Linux somehow — confirm `~/Neocron2/D3D9.dll` does NOT exist; if it does, disable + re-enable the addon to re-stamp |
| **Windows**: game starts but no ReShade overlay | `dxgi.dll` not staged — check launcher's `addon.log` for fetch errors; ensure `7z` is on `PATH` |
| **Windows**: black screen | dgVoodoo `D3D8.dll`/`D3D9.dll` missing or x64 built (the auto-fetch picks x86) |
| **Windows**: ReShade shaders missing | `reshade-shaders/Shaders/` empty — check `addon.log`; the GitHub tarball fetch may have been blocked |
| Game patch broke wrapper | Re-launch the launcher; the post-update hook re-stamps automatically |
| HUD misaligned (Windows) | dgVoodoo resolution forced — set `Resolution = unforced` in `dgVoodoo.conf` |

Logs to check:
- `~/.local/share/neocron-launcher/addons/addon.log` — addon manager (Linux/macOS)
- `%APPDATA%\neocron-launcher\addons\addon.log` — addon manager (Windows)
- `~/Neocron2/logs/error_*.log` — game's own log

## Licenses

- This repo's code, configs, docs: **MIT** (see `LICENSE`)
- `D3D8.dll` / `D3D9.dll` (dgVoodoo2): **freeware**, redistribution
  allowed under the dgVoodoo2 license. Auto-fetched at install time
  from upstream — never redistributed by this repo. Attribution: Dege.
- `dxgi.dll` (ReShade): **BSD 3-Clause**, but upstream asks
  redistributors not to bundle. We don't bundle — auto-fetched from
  <https://reshade.me> to the user's machine at install time.
  Attribution: Patrick Mours.
- `reshade-shaders/`: per upstream — typically MIT/BSD per shader.
  Auto-fetched from <https://github.com/crosire/reshade-shaders> at
  install time, never redistributed by this repo.
- `vkBasalt`: **Zlib**. The launcher does NOT bundle it — users install
  it through their distro package manager. Attribution: DadSchoorse.
