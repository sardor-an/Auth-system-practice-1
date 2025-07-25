# Generated by Django 5.2.3 on 2025-07-24 11:20

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_onetimetokenconfirmation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='smarttoken',
            name='user',
        ),
        migrations.CreateModel(
            name='OneTimeUrl',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('uid64', models.CharField()),
                ('token', models.CharField()),
                ('is_used_once', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='one_time_urls', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='OneTimeTokenConfirmation',
        ),
        migrations.DeleteModel(
            name='SmartToken',
        ),
    ]
