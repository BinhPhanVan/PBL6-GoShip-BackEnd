# Generated by Django 3.2 on 2022-12-10 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserApi', '0009_shipper_home_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipper',
            name='avatar_url',
            field=models.CharField(blank=True, default='https://firebasestorage.googleapis.com/v0/b/pbl6-goship.appspot.com/o/profile_icon.png?alt=media&token=e2229d0c-ce55-4ccb-8b2d-9f66dd5c55ca', max_length=1000, null=True),
        ),
    ]
