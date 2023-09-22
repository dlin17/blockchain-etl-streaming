#!/usr/bin/env bash

gcloud deployment-manager deployments create ethereum-etl-pubsub-arbitrum-test --template deployment_manager_pubsub_ethereum.py
