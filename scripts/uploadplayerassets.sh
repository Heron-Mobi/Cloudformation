#!/bin/bash

REGION=$1

VIDEOBUCKET=$(aws cloudformation describe-stacks --region ${REGION} \
	--stack-name heron-base \
	--query 'Stacks[0].Outputs[?OutputKey==`VideoBucket`].OutputValue' --output text)

for f in player/*; do aws s3 cp $f s3://${VIDEOBUCKET}; done
