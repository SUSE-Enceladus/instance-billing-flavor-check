# instance-billing-type-check
A CLI tool to determine if an instance is PAYG or BYOS across different CSPs

## exit codes
If the instance metadata can be verified successfully the exit code is 10 (PAYG),
however, if the instance metadata is present and the instance metadata reaches
the verification code and is not valid metadata, exit code is 11 (BYOS)

If, while trying to verify the instance metadata, the instance metadata
can not reach the verification code because any other error occurs,
i.e. network issue, metadata not present, etcetera, exit code is 12 (Unknown)
