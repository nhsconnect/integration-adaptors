# Manual deployment
This folder contains files thant need to deployed manualy to AKS cluster after creation
It is only required when the environment is PTL type - connected to HSCN

The pods in cluster need to access both Azure services, and NHS services, and need to be able to resolve DNS names for both at the same time
This requires a custom config for CoreDNS component in AKS, so the `*.nhs.uk` requests are forwarded to nhs DNS servers.

# Steps.
1. SCP the kube-dns.yaml file to testbox instance - you will find the command in Terraform outpput of base compnent
2. SCP the aksconfig file to testbox instance, the file can be obtained by running: `terraform output base_aks_kube_config >> .kubeconfig`
3. SSH to testbox instance.
4. Run `export KUBECONFIG=~/.kubeconfig`
5. Run `kubectl get namespace` to check if kubectl works and connects to AKS cluster
6. Run `kubectl apply -f kube-dns.yaml && kubectl -n kube-system rollout restart deployment coredns`

This shoud now allow proper routing of DNS requests.
