# Certificates for component testing locally only

These certs are used for local testing, which is why they have been checked in.

# fake-spine

Generated via:

```bash
openssl req -x509 -subj "/CN=fakespine" -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365
```

The fake_spine_inbound_outbound_trust.pem file contains public certs for:
- inbound
- outbound


# inbound-cert

Generated via:

```bash
openssl req -x509 -subj "/CN=inbound" -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365
```

The inbound_fake_spine_trust.pem file contains public certs for:
- fakespine

# outbound-cert

Generated via:

```bash
openssl req -x509 -subj "/CN=outbound" -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365
```

The outbound_fake_spine_trust.pem file contains public certs for:
- fakespine