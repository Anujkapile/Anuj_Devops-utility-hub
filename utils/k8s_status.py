from __future__ import annotations

from datetime import datetime, timezone

try:
    from kubernetes import client, config
    from kubernetes.client.rest import ApiException
    _K8S_AVAILABLE = True
except ImportError:
    _K8S_AVAILABLE = False


#def _load_kube_config() -> bool:
 #   """Try in-cluster config first, fall back to kubeconfig file."""
  #  if not _K8S_AVAILABLE:
   #     return False
   # try:
    #    config.load_incluster_config()
     #   return True
   # except Exception:
    #    pass
   # try:
    #    config.load_kube_config(config_file="/etc/rancher/k3s/k3s.yaml")
     #   return True
   # except Exception:
    #    return False

def _load_kube_config() -> bool:
    """Try in-cluster config first, fall back to kubeconfig file."""
    if not _K8S_AVAILABLE:
        return False
    
    import os
    for path in [
        "/root/.kube/config",
        os.path.expanduser("~/.kube/config"),
        "/etc/rancher/k3s/k3s.yaml",
    ]:
        try:
            if os.path.exists(path):
                config.load_kube_config(config_file=path)
                return True
        except Exception:
            continue
    return False

def _age(dt_str: str | None) -> str:
    """Return a human-readable age string from an ISO timestamp."""
    if not dt_str:
        return "unknown"
    try:
        created = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - created
        total = int(delta.total_seconds())
        if total < 60:
            return f"{total}s"
        if total < 3600:
            return f"{total // 60}m"
        if total < 86400:
            return f"{total // 3600}h"
        return f"{total // 86400}d"
    except Exception:
        return "unknown"


def _pod_to_dict(pod) -> dict:
    """Convert a V1Pod object to a serialisable dict."""
    meta = pod.metadata
    spec = pod.spec
    status = pod.status

    # Container statuses
    containers = []
    for cs in (status.container_statuses or []):
        state = cs.state
        state_str = "unknown"
        reason = None
        if state.running:
            state_str = "running"
        elif state.waiting:
            state_str = "waiting"
            reason = state.waiting.reason
        elif state.terminated:
            state_str = "terminated"
            reason = state.terminated.reason

        containers.append(
            {
                "name": cs.name,
                "ready": cs.ready,
                "restart_count": cs.restart_count,
                "state": state_str,
                "reason": reason,
                "image": cs.image,
            }
        )

    # Init container statuses
    init_containers = []
    for ics in (status.init_container_statuses or []):
        init_containers.append(
            {
                "name": ics.name,
                "ready": ics.ready,
                "restart_count": ics.restart_count,
            }
        )

    # Resource requests (from spec)
    resource_requests: dict[str, dict] = {}
    for c in (spec.containers or []):
        if c.resources and c.resources.requests:
            resource_requests[c.name] = dict(c.resources.requests)

    created_at = meta.creation_timestamp.isoformat() if meta.creation_timestamp else None

    return {
        "name": meta.name,
        "namespace": meta.namespace,
        "phase": status.phase,
        "conditions": [
            {"type": cond.type, "status": cond.status}
            for cond in (status.conditions or [])
        ],
        "containers": containers,
        "init_containers": init_containers,
        "node": spec.node_name,
        "pod_ip": status.pod_ip,
        "host_ip": status.host_ip,
        "labels": dict(meta.labels or {}),
        "annotations_count": len(meta.annotations or {}),
        "created_at": created_at,
        "age": _age(created_at),
        "resource_requests": resource_requests,
        "restart_policy": spec.restart_policy,
        "service_account": spec.service_account_name,
    }


def get_k8s_pods(namespace: str = "all", all_namespaces: bool = True) -> dict:
    """
    Return a dict with pod summaries and aggregate counts.

    Args:
        namespace:      Target namespace (ignored if all_namespaces=True).
        all_namespaces: If True, list pods across all namespaces.

    Returns:
        {
          "pods":      [...],
          "summary":   { running, pending, failed, succeeded, unknown, total },
          "namespace": str,
          "error":     None | str,
        }
    """
    if not _K8S_AVAILABLE:
        return {
            "pods": [], "summary": {}, "namespace": namespace,
            "error": "kubernetes Python package is not installed. Run: pip install kubernetes",
        }

    if not _load_kube_config():
        return {
            "pods": [], "summary": {}, "namespace": namespace,
            "error": "Could not load Kubernetes config (neither in-cluster nor kubeconfig found).",
        }

    try:
        v1 = client.CoreV1Api()
        if all_namespaces:
            pod_list = v1.list_pod_for_all_namespaces(watch=False)
        else:
            pod_list = v1.list_namespaced_pod(namespace=namespace, watch=False)

        pods = [_pod_to_dict(p) for p in pod_list.items]

        phase_counts: dict[str, int] = {}
        for p in pods:
            phase = (p["phase"] or "Unknown").capitalize()
            phase_counts[phase] = phase_counts.get(phase, 0) + 1

        summary = {
            "total": len(pods),
            "running": phase_counts.get("Running", 0),
            "pending": phase_counts.get("Pending", 0),
            "failed": phase_counts.get("Failed", 0),
            "succeeded": phase_counts.get("Succeeded", 0),
            "unknown": phase_counts.get("Unknown", 0),
        }

        return {
            "total": summary["total"],   # 👈 ADD THIS
            "items": pods,              # 👈 ADD THIS
            "pods": pods,               # (optional, keep for compatibility)
            "summary": summary,
            "namespace": "all" if all_namespaces else namespace,
            "error": None,
        }

    except ApiException as exc:
        return {
            "pods": [], "summary": {}, "namespace": namespace,
            "error": f"Kubernetes API error {exc.status}: {exc.reason}",
        }
    except Exception as exc:
        return {
            "pods": [], "summary": {}, "namespace": namespace,
            "error": str(exc),
        }


def get_namespaces() -> dict:
    """List all namespaces in the cluster."""
    if not _K8S_AVAILABLE:
        return {"namespaces": [], "error": "kubernetes package not installed"}
    if not _load_kube_config():
        return {"namespaces": [], "error": "Could not load Kubernetes config"}
    try:
        v1 = client.CoreV1Api()
        ns_list = v1.list_namespace()
        namespaces = [
            {
                "name": ns.metadata.name,
                "status": ns.status.phase,
                "age": _age(
                    ns.metadata.creation_timestamp.isoformat()
                    if ns.metadata.creation_timestamp else None
                ),
            }
            for ns in ns_list.items
        ]
        return {"namespaces": namespaces, "error": None}
    except Exception as exc:
        return {"namespaces": [], "error": str(exc)}
