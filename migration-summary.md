# I. Executive Technical Summary

- **Project Identity:** A custom, infrastructure-as-code (IaC) deployment of a **hybrid (Linux + Windows) Kubernetes cluster** on Vultr. Because Vultr Kubernetes Engine (VKE) lacks native Windows node support, this system orchestrates a raw RKE2 (Rancher Kubernetes Engine v2) cluster from scratch, complete with a custom Go-based autoscaler.
- **Core Stack:**
  - **Infrastructure:** Terraform (Vultr Provider).
  - **Orchestration:** RKE2 (Kubernetes).
  - **OS Mix:** Ubuntu 22.04 LTS (Control Plane, Linux workers) & Windows Server 2022 (Windows workers, CI, SQL Server).
  - **Networking:** Traefik v3 (Ingress), Flannel VXLAN (CNI).
  - **Custom Tooling:** Go 1.25 (gRPC Autoscaler sidecar), Bash/PowerShell (Bootstrapping).
- **Architecture Pattern:** Hub-and-Spoke VPC Topology with Immutable Infrastructure. Compute nodes are bootstrapped dynamically via `user-data` templates, relying on cloud-init and scheduled tasks rather than post-provisioning configuration management.
- **Key Capabilities:** Hybrid container scheduling, automated TLS via Let's Encrypt (DNS HTTP-01), custom scaling of Windows nodes via tag-matching, and a fully self-managed, optimized SQL Server 2022 instance on block storage.

---

# II. Core Data Structures & State Management

- **Terraform State:** The ultimate source of truth for static infrastructure (VPCs, static IPs, Firewall Groups, initial node pools). State is managed remotely via Terraform Cloud (`mobigic-pepper-advantage/Dev`).
- **Cluster State (etcd):** Managed natively by RKE2 on the control plane. Snapshots are explicitly configured in the bootstrap script to run via cron (`0 */6 * * *`) with a retention of 10.
- **Autoscaler State (Node Groups):** The Go autoscaler relies on a JSON configuration (`node-groups.json`) mounted as a ConfigMap. It matches Kubernetes node requests to Vultr instances using a strict intersection of Vultr **Tags** (`match_tags`).
- **Ingress Routing State:** Managed entirely via Traefik Custom Resource Definitions (`IngressRoute`, `Middleware`, `TLSOption`). Cross-namespace routing is explicitly enabled to allow Traefik (in the `traefik` namespace) to resolve services in `default`.

---

# III. Module-Level Logic & Implementation Details

### 1. Infrastructure Provisioning (`*.tf` files)

- **Purpose:** Provisions raw Vultr compute, network, and storage primitives.
- **Internal Logic:**
  - **Network (`03-network.tf`):** Defines a `10.0.0.0/20` VPC. Notably, it creates a Vultr Load Balancer that forwards TCP traffic directly to predefined Kubernetes **NodePorts (30080 for HTTP, 30443 for HTTPS)**. This bypasses the need for the Vultr Cloud Controller Manager (CCM), which is incompatible with RKE2's immutable `rke2://` provider ID.
  - **Kubernetes Nodes (`05-kubernetes.tf`):** Provisions a single Linux Control Plane, a pool of Linux workers, and a single initial Windows worker. Inject scripts via `user_data` to bootstrap RKE2.
  - **Database (`04-database.tf`):** Provisions a Windows VM with an attached 1TB block storage volume, configured to run an unattended installation of MSSQL 2022.

### 2. Node Bootstrapping & OS Tuning (`scripts/`)

- **Purpose:** Bridges the gap between a raw OS and a functioning Kubernetes node/database server.
- **Linux Agent/Server Logic (`rke2-*.sh.tpl`):**
  - **DNS Hack:** Vultr's DHCP provides 4 nameservers, but `resolv.conf` maxes at 3. The script forces a `systemd-resolved` drop-in to cap DNS at 3 IPs, preventing continuous `kubelet` log spam.
  - **Firewall Annihilation:** Explicitly disables `firewalld` and `ufw`. RKE2's CNI (Flannel/Canal) manages its own `iptables` rules. Leaving OS firewalls enabled causes race conditions that silently break pod-to-pod networking.
  - **Interface Binding:** Applies a `HelmChartConfig` to force Flannel to use `enp8s0` (the VPC interface). Without this, Flannel binds to the public IP, breaking VXLAN tunnels.
- **Windows Agent Logic (`rke2-windows-agent.ps1.tpl`):**
  - **Metadata API Polling:** Hits Vultr's local metadata IP (`169.254.169.254`) to fetch the internal VPC IP, then manually binds it to the second Ethernet adapter.
  - **Reboot Orchestration:** Windows Containers require a system reboot. The script creates a scheduled task, installs the feature, and reboots. _Crucially, this logic is split into a boot script (`win-install-rke2-boot-script.bat`) to ensure the agent installation resumes automatically after the Terraform-initiated restart._
- **SQL Server Tuning (`install-mssql.ps1.tpl`):**
  - Uses T-SQL to dynamically calculate and set optimal `max server memory` (Total RAM - 2GB for OS).
  - Calculates CPU count to dynamically provision `TempDB` files (1 per CPU core, up to 8).
  - Automatically sets up a PowerShell-driven scheduled task for daily `BACKUP DATABASE` execution with a 7-day retention cleanup loop.

### 3. Custom Vultr Autoscaler (`autoscaler/`)

- **Purpose:** Because Vultr has no native Cluster Autoscaler integration for custom RKE2 clusters, this Go service implements the official Kubernetes `externalgrpc` cloud provider interface.
- **Internal Logic:**
  - Runs as a sidecar container to the official `cluster-autoscaler` binary pod. Communication happens over `localhost:8086` via gRPC.
  - **Scaling Up:** When `NodeGroupIncreaseSize` is called, it reads the target `node-groups.json`, calculates the delta, and executes the `vultr-cli instance create` command via `os/exec`. (It does _not_ use a native REST SDK, it shells out to the CLI).
  - **Discovery:** Matches existing Vultr instances to Kubernetes node groups by intersecting Vultr instance `Tags` with the `match_tags` array in the JSON config.

### 4. Kubernetes Manifests (`manifests/`)

- **Purpose:** Deploys core cluster services.
- **Ingress & TLS:** Uses Traefik. Disables the global HTTP->HTTPS redirect to allow bare-IP Vultr Load Balancer health checks to succeed. HTTP->HTTPS redirection is handled via a Traefik `Middleware` explicitly attached to host-matched `IngressRoutes`.
- **Cert-Manager:** Uses Let's Encrypt `http01` challenges (via Traefik) to provision TLS secrets automatically.

---

# IV. Key Decisions, Nuances, & "The Special Sauce"

- **The Flannel-Over-Calico Necessity:** The code explicitly documents that `cni: flannel` _must_ be used instead of RKE2's default Calico. Calico's `calico-node` DaemonSet is strictly Linux-only. Windows nodes would receive overlay IPs but no routing tables, rendering them unreachable. Flannel VXLAN bundles a Windows plugin natively.
- **Bypassing the Vultr CCM:** Kubernetes usually relies on a Cloud Controller Manager to wire up external Load Balancers. This setup skips it entirely because Vultr's CCM expects standard provider IDs, but RKE2 forces `rke2://`. The workaround is clever: Terraform creates a Layer 4 TCP LB that blindly forwards to Traefik's statically defined `NodePorts`. Traefik is forced to run with `externalTrafficPolicy: Local` to preserve the original client IP.
- **Windows Taints & Tolerations:** The cluster utilizes rigorous node-affinity. Windows nodes are tainted (`os=windows:NoSchedule`), ensuring Linux pods don't accidentally get scheduled on Windows nodes (which would result in catastrophic `ImagePullBackOff` or execution failures).
