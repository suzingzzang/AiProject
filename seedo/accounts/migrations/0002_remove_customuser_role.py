# Generated by Django 5.0.6 on 2024-06-24 02:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("accounts", "0001_initial")]

    operations = [migrations.RemoveField(model_name="customuser", name="role")]
