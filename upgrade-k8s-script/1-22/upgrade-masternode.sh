#!/usr/bin/env bash

COLOR='\033[1;34m'
NC='\033[0m' # No Color


read -p "enter region: (ap-southeast-1)" REGION
read -p "enter AWS profile: " AWS_PROFILE
export AWS_PROFILE=$AWS_PROFILE
if [ -z "$REGION" ]; then
    REGION="ap-southeast-1"
fi

VERSION="1.22"
read -p "enter cluster name: " CLUSTER

echo Checking master nodes of "$CLUSTER"

for i in `aws eks list-nodegroups --cluster-name $CLUSTER --output text|awk {'print $2'}`; do
  printf "\nchecking nodegroup $i"
  NODEGROUP=`aws eks describe-nodegroup --cluster-name "$CLUSTER" --nodegroup-name "$i"`
  CURRENT_VERSION=`echo $NODEGROUP|jq .nodegroup.version|sed -e 's/^"//' -e 's/"$//'`
  echo "current version is $CURRENT_VERSION"
  if [ $CURRENT_VERSION == $VERSION ]; then
    echo "Nodegroup version is up to date"
  else
    echo "Please copy and paste the following command to another terminal and run"
    printf "${COLOR}export AWS_PROFILE=$AWS_PROFILE; eksctl upgrade nodegroup --name $i --cluster $CLUSTER --region $REGION --kubernetes-version $VERSION${NC}"
  fi
done

