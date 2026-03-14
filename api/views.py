from rest_framework.decorators import api_view
from rest_framework.response import Response
import random
import hashlib

CURRENT_CHALLENGE = None
CURRENT_SALT = "abc123"
STORED_PASSWORD = "mypassword"


@api_view(['POST'])
def get_challenge(request):
    global CURRENT_CHALLENGE

    username = request.data.get("username")

    if not username:
        return Response({"error": "Username required"}, status=400)

    CURRENT_CHALLENGE = random.randint(100000, 999999)

    return Response({
        "username": username,
        "salt": CURRENT_SALT,
        "challenge": CURRENT_CHALLENGE
    })


@api_view(['POST'])
def verify_proof(request):
    global CURRENT_CHALLENGE

    username = request.data.get("username")
    proof = request.data.get("proof")

    if not username or not proof:
        return Response({"error": "Missing username or proof"}, status=400)

    if CURRENT_CHALLENGE is None:
        return Response({"error": "No challenge generated"}, status=400)

    # build data string
    data = STORED_PASSWORD + CURRENT_SALT + str(CURRENT_CHALLENGE)

    # expected proof
    expected_proof = hashlib.sha256(data.encode()).hexdigest()

    print("\n----- DEBUG -----")
    print("DATA STRING:", data)
    print("EXPECTED PROOF:", expected_proof)
    print("RECEIVED PROOF:", proof)
    print("-----------------\n")

    if proof == expected_proof:
        return Response({
            "message": "Authentication successful",
            "token": "sample_jwt_token_12345"
        })

    return Response({"error": "Invalid proof"}, status=401)