# Generated by Django 4.2.6 on 2024-02-27 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billapp', '0014_debitnotehistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='debitnoteitem',
            name='itm_hsn',
            field=models.IntegerField(null=True),
        ),
    ]
