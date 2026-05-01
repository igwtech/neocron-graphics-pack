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
| **Linux / macOS (Wine/Proton)** | `vkBasalt` Vulkan post-processing layer with the same ReShade `.fx` shaders, tuned values baked in |

Why two paths? dgVoodoo2's D3D9 wrapper internally calls D3D11, and that
chain hits a known DXVK incompatibility — verified live with v0.2.1, the
game crashes with exit code 5 in a "Init D3D object → Shutdown driver"
loop. vkBasalt sidesteps the issue entirely by hooking at the Vulkan
layer, after DXVK has already done D3D9→Vulkan translation.

The downside of vkBasalt is that it doesn't read ReShade preset files,
so per-uniform tuning has to be **baked into the `.fx` shader files
themselves**. v0.3.1 ships our tuned versions (with attribution) on top
of the upstream pack fetched at install time.

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
| `vkBasalt.conf`, cyberpunk LUT, tuned `.fx` shaders | Linux, macOS | bundled in this repo |
| `D3D8.dll` + `D3D9.dll` (dgVoodoo2 v2.87.1, MS/x86) | Windows | <https://github.com/dege-diosg/dgVoodoo2/releases> |
| `dxgi.dll` (ReShade 6.7.3, 32-bit) | Windows | <https://reshade.me/downloads/ReShade_Setup_6.7.3_Addon.exe> |
| `reshade-shaders/Shaders/` + `Textures/` | All | <https://github.com/crosire/reshade-shaders> (nvidia branch) |
| `qUINT_mxao.fx`, `qUINT_ssr.fx`, etc. | Linux, macOS | <https://github.com/martymcmodding/qUINT> (master, MIT) |

ReShade's authors prefer that binaries not be redistributed — every user
should pull fresh from the official site. Auto-fetch respects that: the
files come from upstream URLs to the user's machine at install time, never
mirrored or hosted by this repo. The exception is the small set of `.fx`
files where we ship our **tuned versions** to override the defaults
(see "Effects shipped" below) — those are MIT/BSD-licensed by upstream
with attribution preserved (see `LICENSE-VENDORED.md`).

## Effects shipped

### Windows (ReShade preset)

`SMAA` + `MXAO` + `Bloom` (cyan-tinted) + `LevelsPlus` (crushed blacks) +
`Vibrance` + `AdaptiveSharpen`. Press **Home** in-game to open the ReShade
overlay and tweak. See `ReShadePreset.ini` for tuning notes.

### Linux / macOS (vkBasalt preset)

Full cyberpunk stack matching the Windows preset, tuning baked into the
shipped `.fx` files since vkBasalt 0.3.2.10 doesn't read
`ReShadePreset.ini`:

```
effects = smaa:mxao:ssdo:ssr:bloom:levelsplus:vibrance:lut:adaptivesharpen
```

| Effect | Source | Role |
|---|---|---|
| `smaa` | vkBasalt built-in | edge-crawl cleanup, threshold 0.05 |
| `mxao` | qUINT_mxao.fx (tuned) | SSAO + SSIL — object grounding, BSP corner shading |
| `ssdo` | PPFX_SSDO.fx (tuned) | directional occlusion stacked on MXAO for sharper edges |
| `ssr` | qUINT_ssr.fx (tuned) | wet-asphalt screen-space reflections |
| `bloom` | Bloom.fx (tuned, cyan-tinted) | neon spill |
| `levelsplus` | LevelsPlus.fx (tuned, gamma 0.40 lift) | midtone compensation for the AO stack |
| `vibrance` | Vibrance.fx (tuned, gentle 0.10) | mild saturation polish |
| `lut` | `neocron_cyberpunk_lut.png` | cool-shadow / magenta-highlight grading |
| `adaptivesharpen` | AdaptiveSharpen.fx (tuned) | final detail recovery |

Press **Home** in-game to toggle the entire chain on/off. The 2D login
screen takes the AO/SSR with no real depth and ends up green-tinted —
toggle off in menus if it bothers you.

#### Tuning your own preset

`tools/build_lut.py` regenerates the cyberpunk LUT from a procedural
recipe (numpy + PIL). Edit the tint magnitudes in the script and re-run
to bake your own grading.

`tools/tune_shaders.py` re-applies our uniform overrides to fresh `.fx`
files. Idempotent, keeps `.fx.orig` backups. Use this if you re-fetch
the upstream shader pack and want to re-bake our tuning.

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
