# Generated by Django 2.0.7 on 2018-08-18 09:11

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('activities', '0011_betauser_signup_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='baby',
            name='parent',
        ),
        migrations.AddField(
            model_name='baby',
            name='parents',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Parents'),
        ),
        migrations.AlterField(
            model_name='betauser',
            name='email',
            field=models.EmailField(help_text='Veuillez saisir votre email pour vous inscrire à la beta', max_length=254, verbose_name='Adresse email'),
        ),
    ]
