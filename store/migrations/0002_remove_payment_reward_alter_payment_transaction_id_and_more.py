# Generated by Django 5.1.5 on 2025-02-08 19:58

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='reward',
        ),
        migrations.AlterField(
            model_name='payment',
            name='transaction_id',
            field=models.CharField(blank=True, default=uuid.uuid4, max_length=100, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='rewardpayment',
            name='payment',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reward_payment', to='store.payment'),
        ),
    ]
