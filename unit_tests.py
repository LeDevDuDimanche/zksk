from PedersenWithParams import *
from petlib.ec import EcGroup, EcPt
from petlib.bn import Bn

# If due to petlib you have a weird configuration of the python interpreter, you can run this like:
# python -m pytest unit_tests.py
# with "python" being the path or alias to the path of your python interpreter that has access to petlib utilities


def test_one_secret_per_generator():
    N = 5
    G = EcGroup(713)
    tab_g = []
    tab_g.append(G.generator())
    for i in range(1, N):
        randWord = randomword(30).encode("UTF-8")
        tab_g.append(G.hash_to_point(randWord))
    o = G.order()
    secrets = []
    for i in range(len(tab_g)):  # we build N secrets
        secrets.append(o.random())# peggy wishes to prove she knows the discrete logarithm equal to this value

    public_info = [
        a * b for a, b in zip(secrets, tab_g)
    ]  # The Ys of which we will prove logarithm knowledge

    pedersen_protocol = PedersenProtocol(
        PedersenVerifier, PedersenProver, public_info, tab_g, secrets
    )
    assert pedersen_protocol.verify()


# can be used to create ec points from hexa
def translate(hexa, group):
    return EcPt.from_binary(bytes(bytearray.fromhex(hexa)), G)





def test_one_generator_one_secret():
    G = EcGroup(713)
    gen = G.generator()
    pp = PedersenProof([gen], ["x1"], [gen])
    prover = pp.getProver({"x1": 1})
    commitments = prover.commit()

    assert len(commitments) == 1


def get_generators(nb_wanted, start_index=0):
    G = EcGroup(713)
    tab_g = []
    tab_g.append(G.generator())
    for i in range(1, nb_wanted):
        randWord = randomword(30).encode("UTF-8")
        tab_g.append(G.hash_to_point(randWord))
    return tab_g


def test_generators_sharing_a_secret():
    N = 10
    generators = get_generators(N)
    unique_secret = 4
    pp = PedersenProof(generators, ["x1"], [g ** unique_secret for g in generators])
    prover = pp.getProver({"x1": unique_secret})
    assert type(prover) == PedersenProver
    commitments = prover.commit()
    assert type(commitment) == type(Bn)

def create_public_info(generators, secrets):
    sum_ = generators[0].group.infinite()
    for i in range(len(generators)):
        sum_ = sum_ + secrets[i] * generators[i]
    return sum_

def test_get_many_different_provers():
    N = 10
    generators = get_generators(N)
    prefix = "secret_"
    secrets_names = [prefix + str(i) for i in range(N)]
    secrets_vals = range(N)
    pp = PedersenProof(generators, secrets_names, create_public_info(generators, secrets_vals))
    prover = pp.getProver(dict(zip(secrets_names, secrets_vals)))
    commitment = prover.commit()
    assert type(commitment) == type(Bn)


def test_same_random_in_commitment():
    g = get_generators(1)[0]
    gens = [g, g, g]
    
    pub_info = create_public_info(gens, [100, 100, 100]) 

    pp = PedersenProof(gens, ["x1", "x1", "x1"], pub_info)
    prover = pp.getProver({"x1": 100})
    commitments = prover.commit()
    first_c = commitments[0]
    for c in commitments:
        assert c == first_c


def test_and_proofs():
    n1 = 3
    n2 = 4
    generators1 = get_generators(n1)
    generators2 = get_generators(n2, start_index=n1)

    secrets_dict = dict([
        ("x0", 1),
        ("x1", 2),
        ("x2", 5),
        ("x3", 100),
        ("x4", 43),
        ("x5", 10)
    ])
    
    sum_1 = create_public_info(generators1, [secrets_dict["x0"], secrets_dict["x1"], secrets_dict["x2"]])

    secrets_2 = [secrets_dict["x0"]]
    for i in range(3, 6):
        secrets_2.append(secrets_dict["x"+str(i)])

    sum_2 = create_public_info(generators2, secrets_2)
    pp1 = PedersenProof(generators1, ["x0", "x1", "x2"], sum_1)

    pp2 = PedersenProof(generators2,
                        ["x0", "x3", "x4", "x5"], sum_2)  #one shared secret x0
    and_proof = AndProof(pp1, pp2)
    and_prover = and_proof.getProver(secrets_dict)
    and_verifier = and_proof.getVerifier()

    commitment = and_prover.commit()
    challenge = and_verifier.sendChallenge(commitment)
    response = and_prover.computeResponse(challenge)
    assert and_verifier.verify(response)