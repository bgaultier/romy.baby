# Generated by Django 2.0.7 on 2018-07-24 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0003_auto_20180724_2358'),
    ]

    operations = [
        migrations.AddField(
            model_name='baby',
            name='feeding_period',
            field=models.PositiveSmallIntegerField(blank=True, default=None, help_text='Veuillez indiquer la période entre chaque biberon', null=True, verbose_name='Période entre chaque biberon'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='quantity',
            field=models.PositiveSmallIntegerField(blank=True, default=None, help_text='Veuillez indiquer la quantité souhaitée', null=True, verbose_name='Quantité'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='type',
            field=models.CharField(choices=[('BOTT', 'Biberon'), ('FEED', 'Manger'), ('DIAP', 'Couche'), ('SLEE', 'Dodo')], help_text="Veuillez indiquer le type de l'activité", max_length=4),
        ),
    ]
