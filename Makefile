.DEFAULT_GOAL=help

REGION=eu-central-1

.PHONY: help
help:
	@echo 'Usage: make <target>'
	@echo 'targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: createbase
createbase:  ## builds base
	./scripts/deploy.sh heron-base cloudformation/01base.yml ${REGION} parameters/base.json


.PHONY: createsignal
createsignal:  ## builds signal sqs
	./scripts/deploy.sh heron-signal cloudformation/02signal.yml ${REGION}

.PHONY: createsignalemail
createsignalemail:  ## builds signal email
	./scripts/deploy.sh heron-signal-email cloudformation/03signal-email.yml ${REGION} parameters/03email.json

.PHONY: createsignaltwitter
createsignaltwitter:  ## builds signal email
	./scripts/deploy.sh heron-signal-twitter cloudformation/03signal-twitter.yml ${REGION}

.PHONY: buildcore
buildcore: | createbase createsignal ## wait builds core in order

.PHONY: buildsignalers
buildsignalers: createsignalemail createsignaltwitter


.PHONY: all
all: | buildcore buildsignalers

