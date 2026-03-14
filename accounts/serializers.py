from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    salt = serializers.CharField()
    verifier = serializers.CharField()


class ChallengeSerializer(serializers.Serializer):
    username = serializers.CharField()


class VerifySerializer(serializers.Serializer):
    proof = serializers.CharField()


class RefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()