# Kubernetes Setup Guide (K3s + NVIDIA GPU Operator)

This guide covers installing K3s, the NVIDIA GPU Operator, and NGINX Ingress Controller on the DGX Spark for deploying the agent-skill-adapter stack.

## Prerequisites

- DGX Spark with GB10 GPU, CUDA 13.0, Ubuntu 24.04
- NVIDIA Container Toolkit 1.18.2+ installed (`nvidia-container-runtime` available)
- Helm v3.20+ installed

## Step 1: Install K3s

K3s uses containerd by default. It **automatically detects** the NVIDIA Container Toolkit and configures the `nvidia` runtime handler — no manual containerd config is needed.

```bash
curl -sfL https://get.k3s.io | sudo INSTALL_K3S_EXEC="--write-kubeconfig-mode 644 --disable=traefik" sh -
```

- `--write-kubeconfig-mode 644`: Makes kubeconfig readable without sudo
- `--disable=traefik`: We use NGINX Ingress instead
- **Do NOT use `--docker`** — K3s's containerd auto-detects nvidia runtime; Docker mode doesn't support RuntimeClass which the GPU Operator requires

Verify nvidia runtime was auto-detected:

```bash
sudo grep nvidia /var/lib/rancher/k3s/agent/etc/containerd/config.toml
```

> **Note**: Docker NVIDIA runtime config (`/etc/docker/daemon.json`) is separate and not used by K3s containerd. It's only needed if using Docker directly.

## Step 2: Configure kubectl

```bash
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
echo 'export KUBECONFIG=/etc/rancher/k3s/k3s.yaml' >> ~/.bashrc
```

Verify:

```bash
kubectl get nodes
# NAME         STATUS   ROLES           AGE   VERSION
# spark-b0f2   Ready    control-plane   ...   v1.34.3+k3s1
```

## Step 3: Install NVIDIA GPU Operator

The GPU Operator manages GPU device plugins and monitoring. Version 25.10.0+ is required for DGX Spark (GB10) support.

```bash
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update
helm install gpu-operator nvidia/gpu-operator \
  --namespace gpu-operator --create-namespace \
  --version v25.10.1 \
  --set driver.enabled=false \
  --set toolkit.enabled=false
```

- `driver.enabled=false`: NVIDIA driver already installed (580.126.09)
- `toolkit.enabled=false`: NVIDIA Container Toolkit already installed (1.18.2)

**IMPORTANT**: GPU Operator versions before v25.10.0 will crash on DGX Spark due to unsupported unified memory queries on the GB10 GPU.

Verify GPU is advertised (may take 2-5 minutes for all pods to start):

```bash
kubectl -n gpu-operator get pods
kubectl get nodes -o json | jq '.items[].status.allocatable["nvidia.com/gpu"]'
# Should return "1"
```

Test GPU access in a pod:

```bash
kubectl run gpu-test --rm -it --restart=Never \
  --image=nvidia/cuda:13.0.1-base-ubuntu24.04 \
  --limits='nvidia.com/gpu=1' -- nvidia-smi
```

## Step 4: Install NGINX Ingress Controller

```bash
helm upgrade --install ingress-nginx ingress-nginx \
  --repo https://kubernetes.github.io/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --set controller.service.type=LoadBalancer
```

K3s ServiceLB binds ports 80/443 to the host, so services are accessible at `http://spark-b0f2.local/`.

## Step 5: Deploy the Stack

Deploy TGI and the full skill-adapter stack via Helm:

```bash
cd ~/agent-skill-adapter
helm install tgi charts/tgi/
# Or deploy everything via umbrella chart:
helm dependency build charts/skill-adapter/
helm install skill-adapter charts/skill-adapter/ --namespace skill-adapter --create-namespace
```

## Ingress Routes

The ingress chart (`charts/ingress/`) provides path-based routing on `spark-b0f2.local`:

| Path | Service | Port |
|------|---------|------|
| `/skill-adapter-frontend` | frontend | 3000 |
| `/skill-adapter-api` | api | 8000 |
| `/skill-adapter-inference` | tgi | 8080 |

Access from your Mac:

```bash
curl http://spark-b0f2.local/skill-adapter-inference/v1/models
curl http://spark-b0f2.local/skill-adapter-api/health
curl http://spark-b0f2.local/skill-adapter-frontend/
```

## Uninstall

```bash
# Remove deployments
helm uninstall skill-adapter -n skill-adapter
helm uninstall tgi
helm uninstall ingress-nginx -n ingress-nginx
helm uninstall gpu-operator -n gpu-operator

# Remove K3s entirely
sudo /usr/local/bin/k3s-uninstall.sh
```

## Troubleshooting

### GPU Operator pods stuck in Init
- Ensure K3s is using containerd (NOT `--docker`) so RuntimeClass `nvidia` works
- Verify nvidia runtime is detected: `sudo grep nvidia /var/lib/rancher/k3s/agent/etc/containerd/config.toml`
- Restart K3s: `sudo systemctl restart k3s`

### GPU Operator pods crashing
- Ensure version is v25.10.0+ (required for GB10/DGX Spark)
- Check logs: `kubectl -n gpu-operator logs <pod-name>`

### Node shows 0 GPU resources
- Check device plugin pod: `kubectl -n gpu-operator get pods | grep device-plugin`
- Check device plugin logs: `kubectl -n gpu-operator logs -l app=nvidia-device-plugin-daemonset`
- Restart K3s: `sudo systemctl restart k3s`

### K3s not starting
- Check logs: `sudo journalctl -u k3s -f`
- Verify containerd is healthy: K3s bundles its own containerd

### CNI not ready after K3s restart
- This is usually transient — wait 30-60 seconds
- If persistent, check flannel: `kubectl -n kube-system get pods | grep flannel`

## References

- [K3s Advanced Options](https://docs.k3s.io/advanced) — containerd config, nvidia auto-detection
- [GPU Operator Install Docs](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/getting-started.html)
- [K3s + GPU Operator on DGX Spark](https://forums.developer.nvidia.com/t/local-kubernetes-cluster-with-k3s-on-nvidia-dgx-spark/355772)
- [GPU Operator DGX Spark support (issue #1794)](https://github.com/NVIDIA/gpu-operator/issues/1794)
