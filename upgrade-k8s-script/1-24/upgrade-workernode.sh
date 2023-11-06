for i in `kubectl --context ucommp-dev/ucommp-dev-blue get node -o wide -l karpenter.sh/initialized=true |grep "v1.23.17"| awk {'print $1'}`; do
  echo $i
  kubectl --context ucommp-dev/ucommp-dev-blue cordon $i
done

for i in `kubectl --context ucommp-dev/ucommp-dev-blue get node -o wide -l karpenter.sh/initialized=true |grep "v1.23.17"| awk {'print $1'}`; do
  kubectl --context ucommp-dev/ucommp-dev-blue drain --delete-emptydir-data --ignore-daemonsets $i
  sleep 0;
  kubectl --context ucommp-dev/ucommp-dev-blue delete node $i
done

