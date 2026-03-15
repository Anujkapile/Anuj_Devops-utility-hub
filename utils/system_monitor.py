import psutil
import platform
import time
from datetime import datetime, timedelta


def _bytes_to_gb(value: int) -> float:
    return round(value / (1024 ** 3), 2)


def _bytes_to_mb(value: int) -> float:
    return round(value / (1024 ** 2), 2)


def get_cpu_info() -> dict:
    """Collect CPU usage and frequency details."""
    freq = psutil.cpu_freq()
    per_core = psutil.cpu_percent(percpu=True)
    return {
        "percent": psutil.cpu_percent(interval=0.5),
        "per_core": per_core,
        "core_count_logical": psutil.cpu_count(logical=True),
        "core_count_physical": psutil.cpu_count(logical=False),
        "freq_current_mhz": round(freq.current, 1) if freq else None,
        "freq_max_mhz": round(freq.max, 1) if freq else None,
        "load_avg": [round(x, 2) for x in psutil.getloadavg()] if hasattr(psutil, "getloadavg") else None,
    }


def get_memory_info() -> dict:
    """Collect virtual and swap memory details."""
    vm = psutil.virtual_memory()
    sw = psutil.swap_memory()
    return {
        "virtual": {
            "total_gb": _bytes_to_gb(vm.total),
            "used_gb": _bytes_to_gb(vm.used),
            "available_gb": _bytes_to_gb(vm.available),
            "percent": vm.percent,
            "cached_gb": _bytes_to_gb(getattr(vm, "cached", 0)),
            "buffers_gb": _bytes_to_gb(getattr(vm, "buffers", 0)),
        },
        "swap": {
            "total_gb": _bytes_to_gb(sw.total),
            "used_gb": _bytes_to_gb(sw.used),
            "free_gb": _bytes_to_gb(sw.free),
            "percent": sw.percent,
        },
    }


def get_disk_info() -> list[dict]:
    """Collect info for all mounted, real disk partitions."""
    partitions = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except PermissionError:
            continue
        partitions.append(
            {
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "total_gb": _bytes_to_gb(usage.total),
                "used_gb": _bytes_to_gb(usage.used),
                "free_gb": _bytes_to_gb(usage.free),
                "percent": usage.percent,
            }
        )
    return partitions


def get_network_info() -> dict:
    """Collect network I/O and interface details."""
    io = psutil.net_io_counters()
    interfaces = []
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    for iface, addr_list in addrs.items():
        iface_stats = stats.get(iface)
        ipv4 = next(
            (a.address for a in addr_list if a.family.name == "AF_INET"), None
        )
        interfaces.append(
            {
                "name": iface,
                "ipv4": ipv4,
                "is_up": iface_stats.isup if iface_stats else False,
                "speed_mbps": iface_stats.speed if iface_stats else 0,
            }
        )
    return {
        "bytes_sent_mb": _bytes_to_mb(io.bytes_sent),
        "bytes_recv_mb": _bytes_to_mb(io.bytes_recv),
        "packets_sent": io.packets_sent,
        "packets_recv": io.packets_recv,
        "errors_in": io.errin,
        "errors_out": io.errout,
        "interfaces": interfaces,
    }


def get_top_processes(n: int = 10) -> list[dict]:
    """Return top N processes sorted by CPU usage."""
    procs = []
    for proc in psutil.process_iter(
        ["pid", "name", "cpu_percent", "memory_percent", "status", "username"]
    ):
        try:
            info = proc.info
            procs.append(
                {
                    "pid": info["pid"],
                    "name": info["name"],
                    "cpu_percent": round(info["cpu_percent"] or 0, 2),
                    "memory_percent": round(info["memory_percent"] or 0, 2),
                    "status": info["status"],
                    "username": info["username"],
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    procs.sort(key=lambda p: p["cpu_percent"], reverse=True)
    return procs[:n]


def get_system_info() -> dict:
    """Return static OS / boot info."""
    boot_ts = psutil.boot_time()
    uptime_sec = time.time() - boot_ts
    uptime = str(timedelta(seconds=int(uptime_sec)))
    return {
        "os": platform.system(),
        "os_release": platform.release(),
        "hostname": platform.node(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "boot_time": datetime.fromtimestamp(boot_ts).strftime("%Y-%m-%d %H:%M:%S"),
        "uptime": uptime,
    }


def get_system_stats() -> dict:
    """Aggregate all system metrics into a single response payload."""
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "system": get_system_info(),
        "cpu": get_cpu_info(),
        "memory": get_memory_info(),
        "disks": get_disk_info(),
        "network": get_network_info(),
        "top_processes": get_top_processes(),
    }
