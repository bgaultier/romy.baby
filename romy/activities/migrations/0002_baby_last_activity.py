# Generated by Django 2.0.7 on 2018-07-24 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='baby',
            name='last_activity',
            field=models.DateTimeField(null=True, verbose_name='Dernière activité'),
        ),
    ]
