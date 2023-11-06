K8S_CFG="$HOME/.kube/config"

myProc=()
aws configure list-profiles | grep -v 'terraform' | while IFS=$'\n' read -r line; do myProc+=("${line}"); done

setup_kubeconfig() {
  aws eks list-clusters --profile setel |
    sed 's/[][", :{}]//g; s/clusters//; /^$/d' |
    sort |
    xargs -L 1 -I {} \
      aws eks update-kubeconfig \
      --profile setel \
      --kubeconfig $HOME/.kube/config \
      --alias setel/{} \
      --name {}

  K8S_CTX=()
  kubectl config get-contexts -o name |
    while IFS=$'\n' read -r line; do K8S_CTX+=("${line}"); done
}

remove_psp() {
  for ctx in "${K8S_CTX[@]}"; do
    PSP=()
    kubectl get psp --context="${ctx}" -o name |
      sed 's|podsecuritypolicy.policy/||' |
      grep -v 'eks.privileged' |
      while IFS=$'\n' read -r line; do PSP+=("${line}"); done
    for policy in "${PSP[@]}"; do
      kubectl delete psp "${policy}" --context="${ctx}"
    done
  done
}

for str in "${myProc[@]}"; do
  AWS_PROFILE="$str"
  setup_kubeconfig
  remove_psp
done






