# DevOps Utility Hub - Ansible Automation

## Project Structure

```
ansible-devops/
├── ansible.cfg                    # Ansible configuration
├── site.yml                       # Main playbook
├── inventory/
│   └── hosts.ini                  # Server inventory
├── group_vars/
│   └── all.yml                    # Global variables
├── roles/
│   ├── common/                    # System setup
│   │   └── tasks/main.yml
│   ├── docker/                    # Docker installation
│   │   ├── tasks/main.yml
│   │   └── handlers/main.yml
│   ├── flask_app/                 # App deployment
│   │   └── tasks/main.yml
│   ├── nginx/                     # Reverse proxy
│   │   ├── tasks/main.yml
│   │   ├── handlers/main.yml
│   │   └── templates/
│   │       └── devops-hub.conf.j2
│   └── monitoring/                # Prometheus + Grafana
│       ├── tasks/main.yml
│       ├── handlers/main.yml
│       └── templates/
│           ├── prometheus.yml.j2
│           └── node_exporter.service.j2
└── playbooks/
    └── deploy.yml                 # Quick deploy playbook
```

---

## Prerequisites

```bash
# Install Ansible
pip install ansible

# Verify
ansible --version
```

---

## Setup

### 1. Update Inventory
Edit `inventory/hosts.ini` with your EC2 IPs:
```ini
[devops_hub]
instance1 ansible_host=<Instance1-IP>

[monitoring]
instance3 ansible_host=<Instance3-IP>
```

### 2. Update Variables
Edit `group_vars/all.yml`:
```yaml
github_repo_url: "https://github.com/Anujkapile/Anuj_Devops-utility-hub.git"
```

### 3. Update SSH Key
Edit `ansible.cfg`:
```ini
private_key_file = ~/.ssh/your-key.pem
```

---

## Execution Commands

### Full Setup (All Instances)
```bash
ansible-playbook site.yml
```

### Dry Run (Check Mode)
```bash
ansible-playbook site.yml --check
```

### Setup Only App Server
```bash
ansible-playbook site.yml --limit devops_hub
```

### Setup Only Monitoring
```bash
ansible-playbook site.yml --limit monitoring
```

### Run Specific Tags
```bash
# Only common setup
ansible-playbook site.yml --tags common

# Only Docker
ansible-playbook site.yml --tags docker

# Only Flask App
ansible-playbook site.yml --tags flask_app

# Only Nginx
ansible-playbook site.yml --tags nginx

# Only Monitoring
ansible-playbook site.yml --tags monitoring

# Only Deploy
ansible-playbook site.yml --tags deploy
```

### Quick Redeploy
```bash
ansible-playbook playbooks/deploy.yml
```

### Test Connectivity
```bash
ansible all -m ping
```

### Check Facts
```bash
ansible devops_hub -m setup
```

---

## Service URLs After Deployment

| Service | URL |
|---------|-----|
| DevOps Hub App | http://<Instance1-IP>:5000 |
| DevOps Hub (Nginx) | http://<Instance1-IP>:80 |
| Prometheus | http://<Instance3-IP>:9090 |
| Grafana | http://<Instance3-IP>:3000 |
| Node Exporter | http://<Instance1-IP>:9100/metrics |

---

## Grafana Default Login
```
Username: admin
Password: admin123
```

---

## Tags Reference

| Tag | Description |
|-----|-------------|
| common | System packages & swap |
| docker | Docker installation |
| flask_app | App clone & container |
| nginx | Reverse proxy setup |
| monitoring | Prometheus + Grafana |
| deploy | Quick redeploy only |
| packages | Package installation only |
| node_exporter | Node Exporter only |
| prometheus | Prometheus only |
| grafana | Grafana only |

---

## Troubleshooting

```bash
# Verbose output
ansible-playbook site.yml -v

# Extra verbose
ansible-playbook site.yml -vvv

# Check specific host
ansible instance1 -m ping

# Check Docker on remote
ansible devops_hub -m command -a "docker ps"

# Check Nginx status
ansible devops_hub -m command -a "systemctl status nginx"
```
