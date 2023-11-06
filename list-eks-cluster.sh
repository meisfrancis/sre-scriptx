#!/bin/sh
# v20211007

set -e

AWS_PROFILE="${AWS_PROFILE:=setel}"
KUBECONFIG="${KUBECONFIG:=$HOME/.kube/config}"

configure() {
  printf "Enter AWS_PROFILE ($AWS_PROFILE): "
  read AWS_PROFILE_INPUT
  if [ ! -z $AWS_PROFILE_INPUT ]
  then
    AWS_PROFILE=$AWS_PROFILE_INPUT
  fi

  printf "Enter KUBECONFIG ($KUBECONFIG): "
  read KUBECONFIG_INPUT
  if [ ! -z $KUBECONFIG_INPUT ]
  then
    KUBECONFIG=$KUBECONFIG_INPUT
  fi
}

setup_kubeconfig() {
  aws eks list-clusters --profile {your-profile-name} \
    | sed 's/[][", :{}]//g; s/clusters//; /^$/d' \
    | sort \
    | xargs -L 1 -I {} \
        aws eks update-kubeconfig \
          --kubeconfig ~/.kube/config \
          --profile {your-profile-name} \
          --alias {your-profile-name}/{} \
          --name {}

  KUBECONTEXT_SEARCH=$(
    kubectl config get-contexts -o name \
      | head -1
  )atlas.py

  if [ -z $KUBECONTEXT_SEARCH ]
  then
    printf "No context found for \"$KUBECONTEXT\", context switching skipped\n"
  else
    kubectl config use-context $KUBECONTEXT_SEARCH
  fi

  echo "Run 'kubectl config use-context ***' to switch context"

  if [ "$(uname -s)" = "Linux" ]
  then
      case "$(cat /proc/sys/kernel/osrelease)" in
        *[mM][iI][cC][rR][oO][sS][oO][fF][tT]*[wW][sS][lL]*)
          WSL_KUBECONFIG_PATH="${KUBECONFIG%config}wsl"
          cat $KUBECONFIG | sed -e '/command/s/aws/wsl/' -e '/env/s/$/ null/' -e '/args/a\      - aws' -e "/command/i\      - --profile\n      - $AWS_PROFILE" -e '/env/{n;N;d;}' > $WSL_KUBECONFIG_PATH
          echo "Created a copy of kubeconfig for WSL in $WSL_KUBECONFIG_PATH"
          ;;
      esac
  fi
}

printf "kubectl/$(kubectl version --client --short | sed -e 's/.*\(v.*\)/\1/') $(aws --version)\n"
configure
setup_kubeconfig

