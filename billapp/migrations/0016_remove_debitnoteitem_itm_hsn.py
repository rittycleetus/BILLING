# Generated by Django 4.2.6 on 2024-02-27 07:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billapp', '0015_debitnoteitem_itm_hsn'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='debitnoteitem',
            name='itm_hsn',
        ),
    ]
