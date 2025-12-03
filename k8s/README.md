## Start the minikube service and the dashboard for debugging
`minikube start`
`minikube dashboard`
## Apply the keda service (queue-based scaling)
`kubectl apply --server-side -f infra/keda-2.18.1.yaml`
#### Check that keda is working
`kubectl get pods -n keda`
## Apply the application
`kubectl apply -k overlays/minikube`
## Get the local ip
`minikube service olympis-server`
