from django.db import models
from .user import CustomUser
from datetime import datetime

class Payment(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed"),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    amount = models.PositiveIntegerField()
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)   
    is_successful = models.BooleanField(default=False)
    reward = models.PositiveIntegerField(null=True, blank=True, default=0)

    
    box_choice = models.CharField(max_length=10, null=True, blank=True)  # Increased max_length for flexibility
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
    date = models.DateTimeField(auto_now_add=True ) 

    def __str__(self):
        return f"{self.user.username} - {self.transaction_id} - {self.status}"
