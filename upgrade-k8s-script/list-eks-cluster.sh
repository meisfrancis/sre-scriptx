#!/bin/sh
SESSION_LIST="uposp-dev
ufp-dev
shared-dev
ulp-dev
ucommp-dev
setelpay-dev"

printf "environment,cluster\n" > cluster-list.csv
for i in $SESSION_LIST; do
  leapp session start $i
  for j in `aws eks list-clusters --profile $i --output text|awk {'print $2'}`; do
    printf "$i,$j\n" >> cluster-list.csv
  done
done
