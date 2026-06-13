# Infrastructure

## Rebuild from Zero

### 1. Provision VMs (Terraform)
```bash
cd terraform/
terraform init
terraform apply
```

### 2. Apply Talos config
```bash
cd talos/
talosctl apply-config --insecure --nodes <NODE_IP> --file controlplane.yaml
talosctl bootstrap --nodes <NODE_IP>
```

### 3. Install K3s
```bash
cd k3s/
# See install.sh
```

## Prerequisites
- Proxmox / libvirt installed
- Terraform >= 1.x
- talosctl installed
- kubectl installed
