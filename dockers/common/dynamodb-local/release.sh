set -ex
# SET THE FOLLOWING VARIABLES
# docker hub username
USRNAME=nhsdev
# image name
IMAGE=nia-dynamodb-local
# bump version
docker run --rm -v "$PWD":/app treeder/bump patch
version=`cat VERSION`
echo "version: $version"
# run build
docker build -t $USRNAME/$IMAGE:latest -f Dockerfile .
# tag it
docker tag $USRNAME/$IMAGE:latest $USRNAME/$IMAGE:$version
# push it
docker push $USRNAME/$IMAGE:latest
docker push $USRNAME/$IMAGE:$version