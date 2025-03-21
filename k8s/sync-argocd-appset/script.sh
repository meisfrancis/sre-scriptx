BRANCH=master

for parent_appset in $(argocd app list -N argocd -ojson 2> /dev/null|jq '.[]|select(.metadata.name|test("applicationset\\.(ufp|ucommp)\\.aws\\.apse1"))|.metadata.name'|tr -d '"'); do
  echo $parent_appset
  argocd app patch $parent_appset --patch '{"spec": { "source": { "targetRevision": "master" } }}' --type merge
  argocd app sync $parent_appset
  for appset in $(argocd appset list -l argocd.argoproj.io/instance=$parent_appset -ojson 2> /dev/null |jq '.[].spec.generators[0].list.elements[]|select(.name|test("applicationset\\.(ufp|ucommp)-(dev|staging|pre-prod)-blue\\.aws\\.apse1"))|.name'|tr -d '"'); do
    echo $appset
    argocd app sync $appset 2> /dev/null
    for target in $(argocd appset list -l argocd.argoproj.io/instance=$appset -ojson 2> /dev/null |jq '.[].spec as $root| $root.template.metadata.name|split("{{name}}")[1] as $tpl|$root.generators[0].list.elements[]|select(.name|test("istio"))|.name+$tpl'|tr -d '"'); do
      echo $target
      argocd app sync $target 2> /dev/null
    done
  done
done