#!/usr/bin/env bash
# Deploy to LocalStack
cd ../terraform/environments/dev
tflocal init
tflocal apply -auto-approve
