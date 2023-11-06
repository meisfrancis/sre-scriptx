#!/usr/bin/env bash

read -p "enter region: (ap-southeast-1)" REGION
read -p "enter AWS profile: " AWS_PROFILE
export AWS_PROFILE=$AWS_PROFILE
if [ -z "$REGION" ]; then
    REGION="ap-southeast-1"
fi

VERSION="1.23"
read -p "enter cluster name: " CLUSTER

echo Checking version of "$CLUSTER"

CURRENT_VERSION=$(aws eks describe-cluster --name "$CLUSTER" | jq .cluster.version | sed -e 's/^"//' -e 's/"$//')

echo Current version is "$CURRENT_VERSION"

if [[ "$VERSION" == "$CURRENT_VERSION" ]]; then
  echo "The cluster $CLUSTER's version is up to date"
else
  aws eks update-cluster-version --region "$REGION" --name "$CLUSTER" --kubernetes-version "$VERSION"
fi

