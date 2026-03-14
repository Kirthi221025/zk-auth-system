from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import ZKUser, BlacklistedToken
from .serializers import (
    RegisterSerializer,
    ChallengeSerializer,
    VerifySerializer,
    RefreshSerializer
)

import random
import hashlib
import jwt
from datetime import datetime, timedelta


# ==========================================
# REGISTER
# ==========================================
@api_view(['POST'])
def register(request):

    serializer = RegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    username = serializer.validated_data["username"]
    salt = serializer.validated_data["salt"]
    verifier = serializer.validated_data["verifier"]

    if ZKUser.objects.filter(username=username).exists():
        return Response({"error": "User already exists"}, status=400)

    ZKUser.objects.create(
        username=username,
        salt=salt,
        verifier=verifier
    )

    return Response({"message": "User registered successfully"}, status=201)


# ==========================================
# GENERATE CHALLENGE
# ==========================================
@api_view(['POST'])
def get_challenge(request):

    serializer = ChallengeSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    username = serializer.validated_data["username"]

    user = ZKUser.objects.filter(username=username).first()

    if not user:
        return Response({"error": "User not found"}, status=404)

    challenge = random.randint(100000, 999999)

    request.session["challenge"] = challenge
    request.session["username"] = username

    print("\n===== CHALLENGE GENERATED =====")
    print("USERNAME:", username)
    print("SALT:", user.salt)
    print("CHALLENGE:", challenge)
    print("===============================\n")

    return Response({
        "salt": user.salt,
        "challenge": challenge
    })


# ==========================================
# VERIFY PROOF
# ==========================================
@api_view(['POST'])
def verify_proof(request):

    serializer = VerifySerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    proof = serializer.validated_data["proof"]

    username = request.session.get("username")
    challenge = request.session.get("challenge")

    if not username or not challenge:
        return Response({"error": "Session expired"}, status=400)

    user = ZKUser.objects.filter(username=username).first()

    if not user:
        return Response({"error": "User not found"}, status=404)

    # Expected proof
    data_string = user.verifier + str(challenge)
    expected = hashlib.sha256(data_string.encode()).hexdigest()

    print("\n========= VERIFY DEBUG =========")
    print("USERNAME:", username)
    print("VERIFIER:", user.verifier)
    print("CHALLENGE:", challenge)
    print("DATA STRING:", data_string)
    print("EXPECTED PROOF:", expected)
    print("RECEIVED PROOF:", proof)
    print("================================\n")

    if proof != expected:
        return Response({"error": "Invalid proof"}, status=401)

    # ACCESS TOKEN
    access_payload = {
        "username": username,
        "role": user.role,
        "type": "access",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }

    access_token = jwt.encode(
        access_payload,
        settings.SECRET_KEY,
        algorithm="HS256"
    )

    # REFRESH TOKEN
    refresh_payload = {
        "username": username,
        "type": "refresh",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=7)
    }

    refresh_token = jwt.encode(
        refresh_payload,
        settings.SECRET_KEY,
        algorithm="HS256"
    )

    return Response({
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token
    })


# ==========================================
# REFRESH TOKEN
# ==========================================
@api_view(['POST'])
def refresh_token(request):

    serializer = RefreshSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    token = serializer.validated_data["refresh_token"]

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )

        if payload.get("type") != "refresh":
            return Response({"error": "Invalid token type"}, status=401)

        new_access_payload = {
            "username": payload["username"],
            "type": "access",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=15)
        }

        new_access_token = jwt.encode(
            new_access_payload,
            settings.SECRET_KEY,
            algorithm="HS256"
        )

        return Response({"access_token": new_access_token})

    except jwt.ExpiredSignatureError:
        return Response({"error": "Refresh token expired"}, status=401)

    except jwt.InvalidTokenError:
        return Response({"error": "Invalid token"}, status=401)


# ==========================================
# DASHBOARD
# ==========================================
@api_view(['GET'])
def dashboard(request):

    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return Response({"error": "Token required"}, status=401)

    token = auth_header.split(" ")[1]

    if BlacklistedToken.objects.filter(token=token).exists():
        return Response({"error": "Token blacklisted"}, status=401)

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )

        return Response({
            "message": "Welcome to dashboard",
            "user": payload["username"],
            "role": payload["role"]
        })

    except jwt.ExpiredSignatureError:
        return Response({"error": "Token expired"}, status=401)

    except jwt.InvalidTokenError:
        return Response({"error": "Invalid token"}, status=401)


# ==========================================
# LOGOUT
# ==========================================
@api_view(['POST'])
def logout(request):

    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return Response({"error": "Token required"}, status=401)

    token = auth_header.split(" ")[1]

    BlacklistedToken.objects.create(token=token)

    return Response({"message": "Logged out successfully"})


# ==========================================
# ADMIN PANEL
# ==========================================
@api_view(['GET'])
def admin_panel(request):

    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return Response({"error": "Token required"}, status=401)

    token = auth_header.split(" ")[1]

    if BlacklistedToken.objects.filter(token=token).exists():
        return Response({"error": "Token blacklisted"}, status=401)

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )

        if payload.get("role") != "admin":
            return Response({"error": "Admin only"}, status=403)

        return Response({
            "message": "Welcome Admin",
            "user": payload["username"]
        })

    except jwt.ExpiredSignatureError:
        return Response({"error": "Token expired"}, status=401)

    except jwt.InvalidTokenError:
        return Response({"error": "Invalid token"}, status=401)