#! /usr/bin/env bash
(cd jenkins-worker && docker build -t temporary/jenkins-worker:latest .) && packer build jenkins-worker.json
