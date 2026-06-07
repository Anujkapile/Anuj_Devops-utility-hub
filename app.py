from flask import Flask, render_template, request, jsonify
from utils.log_analyzer import analyze_logs, get_log_summary
from utils.system_monitor import get_system_stats
from utils.docker_status import get_docker_containers
from utils.k8s_status import get_k8s_pods

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

# ── Log Analyzer ──────────────────────────────────────────────────────────────

@app.route("/logs")
def logs():
    return render_template("logs.html")

@app.route("/api/logs/analyze", methods=["POST"])
def api_analyze_logs():
    data = request.get_json()
    log_text = data.get("log_text", "")
    level_filter = data.get("level", "ALL")
    keyword = data.get("keyword", "")
    if not log_text.strip():
        return jsonify({"error": "No log content provided"}), 400
    result = analyze_logs(log_text, level_filter=level_filter, keyword=keyword)
    return jsonify(result)

@app.route("/api/logs/summary", methods=["POST"])
def api_log_summary():
    data = request.get_json()
    log_text = data.get("log_text", "")
    if not log_text.strip():
        return jsonify({"error": "No log content provided"}), 400
    summary = get_log_summary(log_text)
    return jsonify(summary)

# ── System Monitor ─────────────────────────────────────────────────────────────

@app.route("/system")
def system():
    return render_template("system.html")

@app.route("/api/system/stats")
def api_system_stats():
    stats = get_system_stats()
    return jsonify(stats)

# ── Docker Status ──────────────────────────────────────────────────────────────

@app.route("/docker")
def docker():
    return render_template("docker.html")

@app.route("/api/docker/containers")
def api_docker_containers():
    containers = get_docker_containers()
    return jsonify(containers)

# ── Kubernetes Status ──────────────────────────────────────────────────────────

@app.route("/kubernetes")
def kubernetes():
    return render_template("kubernetes.html")

@app.route("/api/k8s/pods")
def api_k8s_pods():
    namespace = request.args.get("namespace", "default")
#    pods = get_k8s_pods(namespace=namespace)
    result = get_k8s_pods(namespace=namespace)
  
    if result.get("error"):
        return jsonify({
            "total": 0, "running": 0, "pending": 0,
            "failed": 0, "succeeded": 0, "unknown": 0,
            "pods": [],
            "error": result["error"]
        })

    summary = result.get("summary", {})
    return jsonify({
        "total":     summary.get("total", 0),
        "running":   summary.get("running", 0),
        "pending":   summary.get("pending", 0),
        "failed":    summary.get("failed", 0),
        "succeeded": summary.get("succeeded", 0),
        "unknown":   summary.get("unknown", 0),
        "pods":      result.get("pods", [])
    })
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
