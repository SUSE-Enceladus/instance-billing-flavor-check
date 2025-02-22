# instance-billing-type-check
A CLI tool to determine if an instance is PAYG or BYOS across different CSPs

## exit codes
**10 - PAYG**

	Valid instance metadata verified successfully

**11 - BYOS**

	Not valid instance metadata verified successfully

**12 - BYOS**

        We could not reliably determine the flavor of the instance. The
        instance is labeled as BYOS, the uncertainty of the determination
        is indicated by the different exit code.
