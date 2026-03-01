# Batman Doom – PS Vita Port

A port of **Batman Doom** (the classic Doom II total conversion by ACE Team) to **PS Vita**, powered by the [doomgeneric](https://github.com/ozkl/doomgeneric) engine.

## Features

- Full Batman Doom gameplay on PS Vita
- OPL3 music synthesis (MUS format)
- 16-channel software SFX mixer
- Dual analog stick controls
- Touch-screen weapon selection
- Quick Save/Load (L+R+UP / L+R+DOWN)
- LiveArea integration

## WAD Files Required

You need to provide your own WAD files (not included due to copyright):

1. **`doom2.wad`** – The original Doom II IWAD
2. **`batman.wad`** – The Batman Doom PWAD (from [doomworld.com](https://www.doomworld.com/idgames/themes/batman/batman))

Copy both files to your PS Vita:
```
ux0:/data/batmandoom/doom2.wad
ux0:/data/batmandoom/batman.wad
```

## Controls

| Button | Action |
|--------|--------|
| Left Stick | Move forward/back, strafe |
| Right Stick | Turn left/right |
| D-Pad | Move / navigate menus |
| Cross (X) | Use / Open doors |
| Square | Fire |
| Circle | Strafe modifier |
| Triangle | Automap |
| R Trigger | Fire |
| L Trigger | Run / Weapon cycle modifier |
| Start | Menu (Escape) |
| Select | Enter / Confirm |
| UP | Quick Save (slot 0) |
| DOWN | Quick Load (slot 0) |
| L+D-Pad | Cycle weapons |


## Building

### GitHub Actions (recommended)

1. Push this repository to GitHub
2. Go to **Actions** tab
3. The workflow builds automatically and uploads a `.vpk` artifact
4. Download the VPK from the Actions run

### Local Build

Requires [VitaSDK](https://vitasdk.org/) installed:

```bash
git clone --depth 1 https://github.com/ozkl/doomgeneric.git
cp doomgeneric_vita.c doomgeneric/doomgeneric/
mkdir build && cd build
cmake .. -DCMAKE_TOOLCHAIN_FILE=$VITASDK/share/vita.toolchain.cmake
make -j$(nproc)
```

The output `BatmanDoomVita.vpk` will be in the `build/` directory.

## Installation

1. Transfer `BatmanDoomVita.vpk` to your PS Vita
2. Install with VitaShell
3. Copy `doom2.wad` and `batman.wad` to `ux0:/data/batmandoom/`
4. Launch "Batman Doom" from the LiveArea

## Debug

Debug logs are written to `ux0:/data/batmandoom/debug.log`.

## Credits

- **Batman Doom** – ACE Team (original Doom II total conversion)
- **doomgeneric** – ozkl (portable Doom engine)
- **Nuked OPL3** – Nuke.YKT (OPL3 emulator)
- **VitaSDK** – PS Vita homebrew toolchain

## License

This port code is provided as-is for educational and homebrew purposes. Batman Doom and Doom II are properties of their respective owners.

