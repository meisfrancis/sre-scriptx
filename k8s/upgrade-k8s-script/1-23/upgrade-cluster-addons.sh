#!/bin/sh
#SESSION_LIST="ufp-dev
#ucommp-dev
#setelpay-dev"
#
#for i in $SESSION_LIST; do
#  leapp session start $i
#  for j in `aws eks list-clusters --profile $i --output text|grep blue|awk {'print $2'}`; do
#    aws eks update-addon --profile $i --addon-name vpc-cni --cluster-name $j --addon-version v1.14.1-eksbuild.1 --resolve-conflicts OVERWRITE
#  done
#done

CLUSTER_LIST="dev-data-eks-GIWemjX4
dev-eks-eks-SSl9ZLzM
pre-prod-eks-eks-J7numciz
sandbox-eks-eks-Q43zeZC8
staging-data-eks"

leapp session start shared-dev
for i in $CLUSTER_LIST; do
  echo $i
  aws eks update-addon --profile shared-dev --addon-name vpc-cni --cluster-name $i --addon-version v1.14.0-eksbuild.2 --resolve-conflicts OVERWRITE
done

#
#aws eks update-addon --profile shared-dev --addon-name aws-ebs-csi-driver --cluster-name dev-eks-eks-SSl9ZLzM --addon-version v1.22.0-eksbuild.2 --service-account-role-arn arn:aws:iam::296904546231:role/AmazonEKS_EBS_CSI_DriverRole_Dev_EKS --resolve-conflicts OVERWRITE
