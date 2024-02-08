#!/bin/bash

NAME=$1
TEMPLATE=$2
REGION=$3
if [ -n "$4" ]; then
	PARAMSFILE=" --parameter-overrides file://$4"
else
	PARAMSFILE=""
    
fi

aws cloudformation deploy --stack-name "${NAME}" \
	--region ${REGION} --template-file ${TEMPLATE} \
	--capabilities CAPABILITY_IAM${PARAMSFILE}
