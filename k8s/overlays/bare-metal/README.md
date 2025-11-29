This is not meant to be reproducible on minikube. This is general documentation for what I did to get my GCP Compute Engine Kubernetes cluster up and running.
This is more for myself than others. For a reproducible system, see the minikube files.

One important thing:
The configs are domain and IP specific. Therefore, they will not 'just work'.

After configuring domain and external IP of my VM:
- Clone the repo
- `sudo k3s kubectl apply -f k8s/infra/cert-manager.yaml`
- `sudo k3s kubectl apply -k k8s/overlay/bare-metal`
