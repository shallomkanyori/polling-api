# Generated by Django 5.1.6 on 2025-03-05 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polling_api', '0002_vote'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='ip_hash',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='vote',
            name='session_id',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
