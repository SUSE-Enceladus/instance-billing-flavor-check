# instance-billing-type-check
A CLI tool to determine if an instance is PAYG or BYOS across different CSPs

## exit codes
**10 - PAYG**

	Valid instance metadata verified successfully

**11 - BYOS**

	Not valid instance metadata verified successfully

**12 - Unknown**

	A problem during the verification of the instance metadata,
	it prints BYOS
