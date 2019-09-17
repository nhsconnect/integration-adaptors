# Jenkins worker image

The files in this folder are used to create the image of a Jenkins worker for the Jenkin [amazon-ecs plugin](https://wiki.jenkins.io/display/JENKINS/Amazon+EC2+Container+Service+Plugin).

Usage:
1. Make sure you're logged into AWS with the appropriate credentials on your laptop
2. Run these commands:
```bash
docker build -t temporary/jenkins-worker:latest .
DOCKER_REGISTRY=nameOfDockerRegistry BUILD_TAG=buildTag packer build jenkins-worker.json
```
