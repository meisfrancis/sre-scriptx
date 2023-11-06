#!/usr/bin/env bash

printf "id,username,name,avatar_url,web_url,created_at,access_level\n" > teamtreasury.csv
list_maintainer=`curl -L \
                   --url "https://api.github.com/orgs/setel-engineering/teams/treasury/members?per_page=100&role=maintainer" \
                   -H "Accept: application/vnd.github+json" \
                   -H "Authorization: Bearer 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" \
                   -H "X-GitHub-Api-Version: 2022-11-28" | jq '.[].url'|tr -d '"'`
for i in $list_maintainer; do
    printf "`curl -L \
              --url "$i" \
              -H "Accept: application/vnd.github+json" \
              -H "Authorization: Bearer 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" \
              -H "X-GitHub-Api-Version: 2022-11-28"|jq '[.id,.login,.name,.avatar_url,.html_url,.created_at]|join(",")'|tr -d '"'`,maintainer\n" >> teamtreasury.csv
done
list_member=`curl -L \
                   --url "https://api.github.com/orgs/setel-engineering/teams/treasury/members?per_page=100&role=member" \
                   -H "Accept: application/vnd.github+json" \
                   -H "Authorization: Bearer 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" \
                   -H "X-GitHub-Api-Version: 2022-11-28" | jq '.[].url'|tr -d '"'`
for i in $list_member; do
    printf "`curl -L \
                           --url "$i" \
                           -H "Accept: application/vnd.github+json" \
                           -H "Authorization: Bearer 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" \
                           -H "X-GitHub-Api-Version: 2022-11-28"|jq '[.id,.login,.name,.avatar_url,.html_url,.created_at]|join(",")'|tr -d '"'`,member\n" >> teamtreasury.csv
done
