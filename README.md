# instance-billing-type-check
A CLI tool to determine if an instance is PAYG or BYOS across different CSPs

If the instance metadata could be verified successfully the exit code would be 10 (PAYG),
however, if the instance metadata is present and no error ocurred during its verification
and verification failed, exit code would be 11 (BYOS)

If during the verification ocurred any other error and the metadata could not be verified,
exit code would be 12 (Unknown)
