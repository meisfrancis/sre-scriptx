#!/usr/bin/env bash

KUBE_PROXY=v1.24.17-eksbuild.3
COREDNS=v1.9.3-eksbuild.9
CSI=v1.24.1-eksbuild.1
CNI=v1.15.3-eksbuild.1

read -p "enter cluster name: " CLUSTER_NAME
read -p "enter aws profile: " PROFILE

export AWS_PROFILE=$PROFILE

function get_version_status() {
  aws eks describe-addon --cluster-name "$CLUSTER_NAME" --addon-name $1 --query "addon.[addonVersion,status]" --output text|awk {'print $1"_"$2'}
}

for i in `aws eks list-addons --cluster-name "$CLUSTER_NAME" --output text | awk {'print $2'}`; do
  echo checking $i
  if [ $i = "kube-proxy" ]; then
    if [ `get_version_status $i` = ${KUBE_PROXY}_ACTIVE ]; then
      echo verified successfully
    else
      echo verified failed
    fi
  elif [ $i = "coredns" ]; then
    if [ `get_version_status $i` = ${COREDNS}_ACTIVE ]; then
      echo verified successfully
    else
      echo verified failed
    fi
  elif [ $i = "vpc-cni" ]; then
    if [ `get_version_status $i` = ${CNI}_ACTIVE ]; then
      echo verified successfully
    else
      echo verified failed
    fi
  elif [ $i = "aws-ebs-csi-driver" ]; then
    if [ `get_version_status $i` = ${CSI}_ACTIVE ]; then
      echo verified successfully
    else
      echo verified failed
    fi
  fi
done
