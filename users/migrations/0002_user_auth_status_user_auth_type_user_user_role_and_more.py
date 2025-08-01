# Generated by Django 5.2.3 on 2025-07-17 11:34

import django.core.validators
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='auth_status',
            field=models.CharField(choices=[('NEW', 'NEW'), ('CODE_VERIFIED', 'CODE_VERIFIED'), ('DONE', 'DONE'), ('PHOTO_STEP', 'PHOTO_STEP')], default='NEW', max_length=31),
        ),
        migrations.AddField(
            model_name='user',
            name='auth_type',
            field=models.CharField(choices=[('VIA_EMAIL', 'VIA_EMAIL'), ('VIA_PHONE', 'VIA_PHONE')], default='', max_length=31),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='user_role',
            field=models.CharField(choices=[('ORDINARY', 'ORDINARY'), ('MANAGER', 'MANAGER'), ('ADMIN', 'ADMIN')], default='ORDINARY', max_length=31),
        ),
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.UUIDField(default=uuid.UUID('daf9cb27-0200-44e1-9052-18426ddcf312'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='photo',
            field=models.ImageField(upload_to='user_photos', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpeg', 'png'])]),
        ),
        migrations.AlterField(
            model_name='userconfirmation',
            name='id',
            field=models.UUIDField(default=uuid.UUID('daf9cb27-0200-44e1-9052-18426ddcf312'), primary_key=True, serialize=False),
        ),
    ]
