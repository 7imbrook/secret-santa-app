Setup k8s traefik ingresses (see https://docs.traefik.io/user-guide/kubernetes/)

```
# Reuse this (easy way)
kubectl apply -f https://raw.githubusercontent.com/containous/traefik/master/examples/k8s/traefik-rbac.yaml

# Made some modifications on the daemon set
kubectl apply -f ./spec/traefik-ds.yaml

```

Create basic auth secret using htaccess for traefik UI
Create generic secret for the twilio api and django secrets
