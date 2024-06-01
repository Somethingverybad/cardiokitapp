from django.db import models
from django.contrib.auth.models import User


from django.contrib.auth.models import User

class PatientData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_data')
    date = models.DateField()
    time = models.TimeField()
    spo2 = models.FloatField()
    heart_rate = models.IntegerField()
    body_temperature = models.FloatField()

    def __str__(self):
        return f'{self.user.username} - {self.date} {self.time}'
