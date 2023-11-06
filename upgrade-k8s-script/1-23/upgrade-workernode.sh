for i in `kubectl --context setel/staging-data-eks get node -o wide -l karpenter.sh/initialized=true |grep "v1.22.17"| awk {'print $1'}`; do
  echo $i
  kubectl --context setel/staging-data-eks cordon $i
done

for i in `kubectl --context setel/staging-data-eks get node -o wide -l karpenter.sh/initialized=true |grep "v1.22.17"| awk {'print $1'}`; do
  kubectl --context setel/staging-data-eks drain --delete-emptydir-data --ignore-daemonsets $i
  sleep 120;
  kubectl --context setel/staging-data-eks delete node $i
done

