"""
Proof of knowledge of two discrete logarithms:
PK{ (x0, x1): y = x0 * g0 + x1 * g1 }

WARNING: if you update this file, update the line numbers in the documentation.
"""

from petlib.ec import EcGroup

from zksk import Secret, DLRep

group = EcGroup()

# Create the base points on the curve.
g0 = group.hash_to_point(b"g0")
g1 = group.hash_to_point(b"g1")

# Preparing the secrets.
# In practice, they probably should be big integers (petlib.bn.Bn)
x0 = Secret()
x1 = Secret()

# Set up the proof statement.

# First, compute the value, "left-hand side".
y = 4 * g0 + 42 * g1

# Next, create the proof statement.
stmt = DLRep(y, x0 * g0 + x1 * g1)

# Simulate the prover and the verifier interacting.
prover = stmt.get_prover({x0: 4, x1: 42})
verifier = stmt.get_verifier()

commitment = prover.commit()
challenge = verifier.send_challenge(commitment)
response = prover.compute_response(challenge)
assert verifier.verify(response)

# Non-interactive proof.
nizk = stmt.prove({x0: 4, x1: 42})
stmt.verify(nizk)
