# sysmon

CPU and GPU temperature/usage monitors for aipc (Ryzen 7 9700X + RTX 5070, Ubuntu 24.04, X11).

Generic sensor apps show the CPU but not the GPU here, because NVIDIA exposes nothing
through hwmon. GPU numbers come from `nvidia-smi` (shared reader in `sysmon_gpu.py`) and CPU
temps from `k10temp` (Tctl and Tccd1).

| Tool | What it is |
|---|---|
| `sysmon-hud` | Always-on-top HUD bar (GTK3, since GTK4 dropped keep-above). Drag to move; click to collapse or expand; right-click for the menu. Position, size and collapsed state persist to `~/.config/sysmon-hud.json`. |
| `sysmon-gui` | Full window with history graphs (GTK4) |
| `sysmon [interval]` | Terminal version, default 1 s |

## Install

These live in `~/bin` (on `PATH`). To start the HUD at login:

```bash
cp autostart/sysmon-hud.desktop ~/.config/autostart/
```

The `.desktop` file has an absolute `Exec=` path, so edit it if your home directory differs.

## Limits

- `GPU_INDEX = 0` in `sysmon_gpu.py`: only the first GPU is shown.
- Needs the NVIDIA driver (`nvidia-smi`) and `python3-gi` with GTK3/GTK4.
- `sysmon-hud` relies on X11 keep-above; it won't stay on top under Wayland.
