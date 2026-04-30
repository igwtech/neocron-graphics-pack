# Neocron Graphics Pack — dgVoodoo2 + ReShade

Modernizes the Neocron 2 renderer. Installs into the game directory through the
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
3. The addon is auto-enabled. Launch the game — dgVoodoo2 + ReShade are active.

The launcher composes `WINEDLLOVERRIDES=quartz=n,b;d3d8=n,b;dxgi=n,b`
automatically; no Proton tweaking required.

## Forking and publishing your own version

This repo is the **skeleton** — it does not redistribute the dgVoodoo2 or
ReShade binaries themselves. You drop in upstream binaries, push to your own
GitHub, and the launcher pulls from there.

### 1. Fork or clone

```bash
git clone https://github.com/igwtech/neocron-graphics-pack.git
cd neocron-graphics-pack
```

(Or fork to your own GitHub account if you want to publish a variant.)

### 2. Drop in dgVoodoo2

1. Download the latest from <http://dege.freeweb.hu/> (or
   <https://github.com/dege-diosg/dgVoodoo2/releases>).
2. Extract `MS/x86/D3D8.dll` (NOT x64 — Neocron is 32-bit).
3. Copy it to the repo root as `D3D8.dll`.
4. (Optional) `dgVoodooCpl.exe` lets you tune `dgVoodoo.conf` with a UI.

The included `dgVoodoo.conf` is preconfigured for Neocron:
- Best-available D3D11 backend
- VSync on, triple-buffering
- 16× anisotropic, 8× MSAA
- Resolution unforced (Neocron has hard-coded UI coordinates — overriding
  resolution misaligns HUD/menus). Pick your screen mode in-game instead.

### 3. Drop in ReShade

1. Download "ReShade with full add-on support" from <https://reshade.me>.
2. The installer is the only way to extract `dxgi.dll`. Run it against any
   throwaway D3D11 EXE (e.g. `notepad++.exe`) and pick "DirectX 10/11/12".
3. Find `dxgi.dll` in the throwaway dir, copy it to this repo root.
4. (Optional) verify with `sha256sum dxgi.dll` and pin the hash in
   `CHANGELOG.md` so users can audit.

### 4. Drop in shaders

1. Clone `https://github.com/crosire/reshade-shaders` (the "slim" branch is a
   smaller curated set).
2. Copy its `Shaders/` and `Textures/` into this repo's `reshade-shaders/`.
3. Pick a sane default in `ReShadePreset.ini` — the default enables
   LumaSharpen + SMAA + AmbientLight, which most users will like.

### 5. Verify the layout

```
neocron-graphics-pack/
├── addon.json
├── README.md
├── LICENSE
├── CHANGELOG.md
├── .gitattributes
├── D3D8.dll               <- dgVoodoo2 wrapper (you provide)
├── dgVoodoo.conf          <- preset
├── dxgi.dll               <- ReShade (you provide)
├── ReShade.ini            <- minimal preset
├── ReShadePreset.ini      <- default-enabled effects
└── reshade-shaders/
    ├── Shaders/           <- you provide (.fx files)
    └── Textures/          <- you provide (.png/.dds)
```

Quick sanity check:
```bash
test -f D3D8.dll && test -f dxgi.dll && \
  test -d reshade-shaders/Shaders && echo "Layout OK" || echo "Missing files"
```

### 6. Tag and push

```bash
git add .
git commit -m "v0.1.0 — initial dgVoodoo2 + ReShade pack"
git tag v0.1.0
git push origin main --tags
```

The launcher fetches via `https://api.github.com/repos/<owner>/<repo>/tarball`,
so any public GitHub repo works. The tag is read by `CheckAddonUpdates`.

## How the launcher integrates

When this addon is enabled:

| Mechanism | What happens |
|---|---|
| **DLL drop-in** | `D3D8.dll`, `dxgi.dll`, configs, shader pack are stamped into the game install dir. |
| **Wine DLL overrides** | The `wineDllOverrides: ["d3d8", "dxgi"]` field tells the launcher to add `d3d8=n,b;dxgi=n,b` to `WINEDLLOVERRIDES`. Native-then-builtin means Wine prefers the dropped-in DLLs. |
| **Pristine pool** | Original game files are snapshotted before being overwritten. Disabling the addon restores them — even if other addons stamp the same paths, the launcher's stacked-restore handles layering. |
| **CDN-update safety** | When the launcher patches the game from the official CDN, it un-stamps addons first, lets the updater run on pristine, refreshes the pristine pool, then re-stamps. Wrapper DLLs survive game patches. |

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
| Game starts but no ReShade overlay | `dxgi.dll` not loaded — check `WINEDLLOVERRIDES` includes `dxgi=n,b` |
| Black screen | dgVoodoo `D3D8.dll` mismatch (x64 instead of x86) |
| ReShade shaders missing | `reshade-shaders/` empty — see step 4 |
| Game patch broke wrapper | Re-launch the launcher; the post-update hook re-stamps automatically |
| HUD misaligned | dgVoodoo resolution forced — set `Resolution = unforced` in `dgVoodoo.conf` |

Logs to check (Linux):
- `~/.local/share/neocron-launcher/addons/addon.log` — addon manager
- `~/.local/share/neocron-launcher/prefix/pfx/drive_c/users/...` — Wine path
- `~/Neocron2/logs/error_*.log` — game's own log

## Licenses

- This repo's code, configs, docs: **MIT** (see `LICENSE`)
- `D3D8.dll` (dgVoodoo2): **freeware**, redistribution allowed under the
  dgVoodoo2 license. Attribution: Dege.
- `dxgi.dll` (ReShade): **BSD 3-Clause**. Attribution: Patrick Mours.
- `reshade-shaders/`: per upstream — typically MIT or BSD per shader.
  See `reshade-shaders/LICENSE` if shipping the crosire pack.

If you fork and redistribute, preserve all upstream license notices.
