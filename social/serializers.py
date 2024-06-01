from django.contrib.auth.models import User
from rest_framework import serializers
from .models import PatientData

class PatientDataSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = PatientData
        fields = ['id', 'user', 'date', 'time', 'spo2', 'heart_rate', 'body_temperature', 'username']

    def get_username(self, obj):
        return obj.user.username
