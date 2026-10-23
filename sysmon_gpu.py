"""NVIDIA GPU reader shared by sysmon, sysmon-gui and sysmon-hud.

NVIDIA is not exposed through hwmon on this machine, so everything comes from
nvidia-smi. Persistence mode is enabled, which keeps a query at ~40 ms -- cheap
enough to poll at 1 Hz without NVML bindings.

Note on "util": utilization.gpu is the fraction of the last sample period in
which *any* kernel was running, not how hard the GPU is working. It pins near
100% during SGLang decode even at modest power, so power is the better load
signal once it saturates.
"""
import subprocess
import sys

GPU_INDEX = 0

# (dict key, nvidia-smi field) -- order defines the CSV column order.
FIELDS = (
    ("temp", "temperature.gpu"),
    ("util", "utilization.gpu"),
    ("vram", "memory.used"),          # MiB
    ("vram_total", "memory.total"),   # MiB
    ("power", "power.draw"),          # W
    ("power_limit", "power.limit"),   # W
    ("sm", "clocks.sm"),              # MHz
    ("fan", "fan.speed"),             # %
)

_CMD = ["nvidia-smi", "-i", str(GPU_INDEX),
        "--query-gpu=" + ",".join(f for _, f in FIELDS),
        "--format=csv,noheader,nounits"]

# Why the most recent read_gpu() returned None; None after a good read.
last_error = None

_warned = set()


def _fail(msg, log):
    global last_error
    last_error = msg
    # The callers poll every second; one line on stderr per distinct error.
    if log and msg not in _warned:
        _warned.add(msg)
        print(f"sysmon_gpu: {msg}", file=sys.stderr)
    return None


def _num(s):
    """'[N/A]' / '[Not Supported]' / '' -> None, so callers can show n/a."""
    try:
        return float(s)
    except ValueError:
        return None


def read_gpu(log=True):
    """-> dict with every key in FIELDS (value float, or None if the driver
    could not report it), or None if nvidia-smi could not be queried at all --
    the reason is then in `last_error`. log=False keeps it off stderr, for
    callers that own the terminal.
    """
    global last_error
    try:
        p = subprocess.run(_CMD, capture_output=True, text=True, timeout=3)
    except subprocess.TimeoutExpired:
        return _fail("nvidia-smi timed out after 3 s", log)
    except OSError as e:
        return _fail(f"could not run nvidia-smi: {e}", log)
    if p.returncode != 0:
        # nvidia-smi reports driver errors on stdout, not stderr.
        err = (p.stderr.strip() or p.stdout.strip()).splitlines()
        return _fail(f"nvidia-smi exited {p.returncode}: "
                     f"{err[0] if err else 'no output'}", log)

    lines = p.stdout.strip().splitlines()
    cols = [c.strip() for c in lines[0].split(",")] if lines else []
    if len(cols) != len(FIELDS):
        return _fail(f"expected {len(FIELDS)} fields from nvidia-smi, "
                     f"got {len(cols)}: {p.stdout.strip()!r}", log)
    last_error = None
    return {k: _num(c) for (k, _), c in zip(FIELDS, cols)}
