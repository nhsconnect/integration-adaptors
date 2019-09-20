packer build -except publish pipeline/packer/inbound.json
packer build -except publish pipeline/packer/outbound.json
packer build -except publish pipeline/packer/spineroutelookup.json
packer build -except publish pipeline/packer/scr-web-service.json