This is not meant to be reproducible on minikube. This is general documentation for what I did to get my GCP Compute Engine Kubernetes cluster up and running.
This is more for myself than others. For a reproducible system, see the minikube files.

One important thing:
The configs are domain and IP specific. Therefore, they will not 'just work'. Also, a valid database connection needs to be established for the system to work.

After configuring domain, external IP, and database. Run these in the VM:

- `curl -sfL https://get.k3s.io | sh -`
- Clone the repo
- `sudo k3s kubectl apply -f k8s/infra/cert-manager.yaml`
- `sudo k3s kubectl apply --server-side -f k8s/infra/keda-2.18.1.yaml`
- `sudo k3s kubectl apply -k k8s/overlays/bare-metal`
