# Generated by Django 3.2 on 2022-11-22 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OrderApi', '0003_auto_20221123_0020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='status',
            name='description',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
