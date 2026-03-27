from __future__ import annotations

import docker
from docker.errors import DockerException, NotFound
from datetime import datetime, timezone


def _parse_ports(ports: dict) -> list[str]:
    """Flatten Docker port bindings into human-readable strings."""
    result = []
    for container_port, host_bindings in (ports or {}).items():
        if host_bindings:
            for binding in host_bindings:
                result.append(f"{binding['HostIp']}:{binding['HostPort']} -> {container_port}")
        else:
            result.append(container_port)
    return result


def _format_size(size_bytes: int) -> str:
    if size_bytes < 0:
        return "N/A"
    for unit in ("B", "KB", "MB", "GB"):
        if abs(size_bytes) < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def _container_to_dict(container) -> dict:
    """Convert a docker.models.containers.Container to a serialisable dict."""
    attrs = container.attrs or {}
    state = attrs.get("State", {})
    host_config = attrs.get("HostConfig", {})
    network_settings = attrs.get("NetworkSettings", {})

    # Resource limits
    mem_limit = host_config.get("Memory", 0)
    cpu_quota = host_config.get("CpuQuota", 0)
    cpu_period = host_config.get("CpuPeriod", 100_000) or 100_000

    # Network info
    networks = {
        name: info.get("IPAddress", "")
        for name, info in (network_settings.get("Networks") or {}).items()
    }

    # Uptime
    started_at_str = state.get("StartedAt", "")
    uptime = None
    if started_at_str and state.get("Running"):
        try:
            started_at = datetime.fromisoformat(
                started_at_str.replace("Z", "+00:00").split(".")[0] + "+00:00"
            )
            delta = datetime.now(timezone.utc) - started_at
            hours, rem = divmod(int(delta.total_seconds()), 3600)
            minutes = rem // 60
            uptime = f"{hours}h {minutes}m"
        except Exception:
            uptime = started_at_str

    return {
        "id": container.short_id,
        "full_id": container.id,
        "name": container.name,
        "image": container.image.tags[0] if container.image.tags else attrs.get("Config", {}).get("Image", "unknown"),
        "status": container.status,  # running, exited, paused, restarting, …
        "state": {
            "running": state.get("Running", False),
            "paused": state.get("Paused", False),
            "restarting": state.get("Restarting", False),
            "exit_code": state.get("ExitCode"),
            "error": state.get("Error", ""),
            "started_at": started_at_str,
            "finished_at": state.get("FinishedAt", ""),
        },
        "uptime": uptime,
        "ports": _parse_ports(network_settings.get("Ports", {})),
        "networks": networks,
        "resource_limits": {
            "memory_limit": _format_size(mem_limit) if mem_limit else "unlimited",
            "cpu_quota": f"{cpu_quota / cpu_period:.2f} cores" if cpu_quota > 0 else "unlimited",
        },
        "labels": attrs.get("Config", {}).get("Labels") or {},
        "restart_policy": host_config.get("RestartPolicy", {}).get("Name", "no"),
    }


def get_docker_containers(all_containers: bool = True) -> dict:
    """
    Return a dict with a list of container summaries and aggregate stats.

    Args:
        all_containers: If True include stopped/exited containers too.

    Returns:
        {
          "containers": [...],
          "summary": { running, stopped, paused, total },
          "error": None | str,
        }
    """
    try:
        client = docker.from_env()
        containers = client.containers.list(all=all_containers)
        container_list = [_container_to_dict(c) for c in containers]

        summary = {
            "total": len(container_list),
            "running": sum(1 for c in container_list if c["state"]["running"]),
            "stopped": sum(1 for c in container_list if not c["state"]["running"] and not c["state"]["paused"]),
            "paused": sum(1 for c in container_list if c["state"]["paused"]),
        }

        return {"containers": container_list, "summary": summary, "error": None}

    except DockerException as exc:
        return {
            "containers": [],
            "summary": {"total": 0, "running": 0, "stopped": 0, "paused": 0},
            "error": str(exc),
        }


def get_container_logs(container_id: str, tail: int = 100) -> dict:
    """Fetch the last *tail* lines of a container's logs."""
    try:
        client = docker.from_env()
        container = client.containers.get(container_id)
        raw_logs = container.logs(tail=tail, timestamps=True).decode("utf-8", errors="replace")
        return {"container_id": container_id, "logs": raw_logs, "error": None}
    except NotFound:
        return {"container_id": container_id, "logs": "", "error": f"Container '{container_id}' not found"}
    except DockerException as exc:
        return {"container_id": container_id, "logs": "", "error": str(exc)
                }
    

def get_docker_status():
    try:
        client = docker.DockerClient(
            base_url='unix:///var/run/docker.sock'
        )
        containers = client.containers.list(all=True)
        return [{
            "name": c.name,
            "status": c.status,
            "image": c.image.tags[0] if c.image.tags else "unknown",
            "id": c.short_id
        } for c in containers]
    except Exception as e:
        return [{"error": "Docker error: " + str(e)}]
