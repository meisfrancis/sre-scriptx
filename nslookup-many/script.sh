FILE_NAME="$1"
if [ -n "$FILE_NAME" ]; then
  rm "$FILE_NAME"
fi

touch "$FILE_NAME"

KUBE_CONFIG=$2

i=3;
for arg in "${@:3}"
do
  LB_LIST_STR=$(kubectl \
  --kubeconfig "$HOME/.kube/$KUBE_CONFIG" \
  -n istio-system \
  get svc \
  -l operator.istio.io/component=IngressGateways \
  -o=jsonpath="{.items[*].status.loadBalancer.ingress[*].hostname}" \
  --context "$arg")
  read -ra LB_LIST <<< $LB_LIST_STR
  for lb in "${LB_LIST[@]}"; do
    echo "$lb" >> "$FILE_NAME"
    dig +short "$lb" >> "$FILE_NAME"
  done
  i=$((i+1))
done

