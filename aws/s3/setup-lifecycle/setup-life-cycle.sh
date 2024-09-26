LIFECYCLE_ID=Archival

cat <<e > lifecycle.json
{
  "Rules": [
    {
      "ID": "$LIFECYCLE_ID",
      "Filter": {},
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 0,
          "StorageClass": "GLACIER"
        }
      ]
    }
  ]
}
e
export AWS_PROFILE=$1
BUCKETS=""
for i in `aws s3api list-buckets|jq '.Buckets[].Name'|sed 's/"//g'`; do
  if [[ `aws s3api list-objects-v2 --bucket $i --max-items 1 | jq '.Contents'` != "null" ]]
  then
    if [[ $(aws s3api get-bucket-lifecycle-configuration --bucket $i 2> /dev/null|jq '.Rules[0].ID'|sed 's/"//g') != ${LIFECYCLE_ID} ]]
    then
      aws s3api put-bucket-lifecycle-configuration --bucket $i --lifecycle-configuration file://lifecycle.json
    fi
  fi
done

echo 'Update Completed'
