# Generated by Django 4.1.13 on 2024-01-24 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='isEmailConfirmado',
            field=models.BooleanField(default=False),
        ),
    ]
