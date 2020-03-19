The certificates in this directory are obtained from the PTL-integration environment.

In order to get newer ones:
1. SSH to a bastion host which has PTL-integration connectivity.
2. Get the `SMSP` certificate by running:
```
openssl s_client -connect simple-sync.int.spine2.ncrs.nhs.uk:443 -showcerts
```
3. Get the `SDS` certificate by running:
```
openssl s_client -connect ldap.nis1.national.ncrs.nhs.uk:636 -showcerts
```
4. Put the first certificate from each of these servers to the files in this repo.
