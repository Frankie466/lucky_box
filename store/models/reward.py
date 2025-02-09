from django.db import models
from .user import CustomUser
from datetime import datetime

class RewardPayment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    amount = models.PositiveIntegerField()  # Amount of reward or prize
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True) 
    is_successful = models.BooleanField(default=False)
    reward = models.PositiveIntegerField(null=True, blank=True, default=0)



    # Reference Payment using string to avoid circular import issues
    payment = models.OneToOneField(
        "store.Payment",  # Ensure "store" matches your Django app name
        on_delete=models.CASCADE,
        related_name="reward_payment",
        null=True,
        blank=True
    )
    
    date = models.DateTimeField(auto_now_add=True ) 

    def __str__(self):
        return f"{self.user.username} - {self.transaction_id} - {'Success' if self.is_successful else 'Failed'}"
