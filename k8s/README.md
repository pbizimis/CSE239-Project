kubectl apply --server-side -f infra/keda-2.18.1.yaml
kubectl get pods -n keda

kubectl apply -k overlays/minikube


