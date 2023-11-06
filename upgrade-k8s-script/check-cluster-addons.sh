#!/bin/sh
SESSION_LIST="ufp-dev
shared-dev
ucommp-dev
setelpay-dev"

printf "environment,cluster\n" > has-ebs-list.csv
for i in $SESSION_LIST; do
  leapp session start $i
  for j in `aws eks list-clusters --profile $i --output text|awk {'print $2'}`; do
    if [ `aws eks list-addons --cluster-name $j --profile $i --output text | awk {'print $2'}|grep aws-ebs-csi-driver` ]; then
      printf "$i,$j\n" >> has-ebs-list.csv
    fi
  done
done
