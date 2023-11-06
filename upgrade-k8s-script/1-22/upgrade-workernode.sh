#!/usr/bin/env bash

COLOR='\033[1;34m'
NC='\033[0m' # No Color


read -p "enter AWS profile: " AWS_PROFILE
read -p "enter K8s context: " CONTEXT
export AWS_PROFILE=$AWS_PROFILE

kubectx $CONTEXT

VERSION="v1.21.14"
for i in `kubectl get node -o wide -l karpenter.sh/initialized=true |grep "$VERSION"| awk {'print $1'}`; do
  echo $i
  kubectl cordon $i
done

for i in `kubectl get node -o wide -l karpenter.sh/initialized=true |grep "$VERSION"| awk {'print $1'}`; do
  kubectl drain --delete-emptydir-data --ignore-daemonsets $i
  sleep 120;
  kubectl delete node $i
done

