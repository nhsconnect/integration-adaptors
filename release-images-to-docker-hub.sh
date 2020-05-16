docker tag local/mhs-outbound:latest nhsdev/nia-mhs-outbound:0.0.1
docker tag local/mhs-inbound:latest nhsdev/nia-mhs-inbound:0.0.1
docker tag local/mhs-route:latest nhsdev/nia-mhs-route:0.0.1

docker tag local/mhs-outbound:latest nhsdev/nia-mhs-outbound:latest
docker tag local/mhs-inbound:latest nhsdev/nia-mhs-inbound:latest
docker tag local/mhs-route:latest nhsdev/nia-mhs-route:latest

docker push nhsdev/nia-mhs-outbound:0.0.1
docker push nhsdev/nia-mhs-outbound:latest
docker push nhsdev/nia-mhs-inbound:0.0.1
docker push nhsdev/nia-mhs-inbound:latest
docker push nhsdev/nia-mhs-route:0.0.1
docker push nhsdev/nia-mhs-route:latest
