# Generated by Django 5.1 on 2024-12-27 23:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='identity_type',
            field=models.CharField(blank=True, choices=[("Driver's Licence", "Driver's Licence"), ('National Identity Number', 'National Identity Number'), ('International Passport', 'International Passport')], max_length=200, null=True),
        ),
    ]
