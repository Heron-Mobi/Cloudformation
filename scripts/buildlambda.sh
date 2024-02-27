#!/bin/bash
REGION=$1
currenttime=$(date +%s) #!TODO change to git sha
aws ssm put-parameter --type String --name /heron/latest/lambda-build \
	--region ${REGION} --value ${currenttime} --overwrite
cd lambdas
PWD=$(pwd)
destination=$(mktemp -d)
for dir in ${PWD}/*
do

	cd ${dir}
	if [ -d build ]; then rm -rf build; fi
	mkdir build
	cp -rf src/* build/.
	cd build && \
	pip install -r requirements.txt -t . && \
	name=$(basename ${dir})
	mkdir -p ${destination}/${name}/${currenttime}
	zip -qr9 ${destination}/${name}/${currenttime}/index.zip *
	cd ..
	rm -rf build
	cd ..
done
echo ${destination}
bucket=$(aws cloudformation describe-stacks --region eu-central-1 \
        --stack-name heron-bootstrap \
	--query 'Stacks[0].Outputs[0].OutputValue' --output text)
cd ${destination}
aws s3 cp --recursive . s3://${bucket}/lambdas
