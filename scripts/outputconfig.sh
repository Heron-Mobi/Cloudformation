#!/bin/bash

REGION=$1

BASE=$(aws cloudformation describe-stacks --region ${REGION} \
	--stack-name heron-base \
	--query 'Stacks[0].Outputs[*]' | jq '.[] | { (.OutputKey) : .OutputValue }' | jq -s add)
#echo $BASE

SIGNAL=$(aws cloudformation describe-stacks --region ${REGION} \
	--stack-name heron-signal \
	--query 'Stacks[0].Outputs[*]' | jq '.[] | { (.OutputKey) : .OutputValue }' | jq -s add )

echo "$SIGNAL $BASE" | jq -s add > /tmp/heronconfig.json
