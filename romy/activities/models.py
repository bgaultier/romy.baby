# coding: utf-8

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

import uuid

class Baby(models.Model):
    first_name = models.CharField(_(u'Prénom'), help_text=_('Veuillez saisir le prénom de votre enfant'), max_length=32, default=_('Romy'))
    parent = models.ForeignKey(User, verbose_name=_('Parent'), on_delete=models.CASCADE)
    feeding_period = models.PositiveSmallIntegerField(_('Période entre chaque biberon'), help_text=_("Veuillez indiquer la période entre chaque biberon"), default=60, null=True, blank=True)

    api_key = models.CharField(_("Clé d'API"), max_length=36, unique=True)

    last_activity = models.DateTimeField(_('Dernière activité'), null=True)

    def __str__(self):
        return self.first_name

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.generate_api_key()
        return super(Baby, self).save(*args, **kwargs)

    def generate_api_key(self):
        self.api_key = uuid.uuid4()
        self.last_activity = timezone.now()

    def belongs_to(self, user):
        return user == self.user

    class Meta:
        verbose_name = _('Bébé')
        verbose_name_plural = _('Bébés')

class Activity(models.Model):
    baby = models.ForeignKey(Baby, on_delete=models.CASCADE)
    EVENT_TYPES = (
        ('BOTTLE', _(u'Biberon')),
        ('BATH', _(u'Bain')),
        ('PEE', _(u'Pipi')),
        ('POOH', _(u'Popo')),
        ('SLEEP', _(u'Dodo')),
    )
    type = models.CharField(max_length=6, help_text=_("Veuillez indiquer le type de l'activité"), choices=EVENT_TYPES)
    quantity = models.PositiveSmallIntegerField(_("Quantité"), help_text=_("Veuillez indiquer la quantité de lait bu par bébé"), default=None, null=True, blank=True)
    comment = models.TextField(_("Commentaire"), max_length=1024, blank=True)

    created_date = models.DateTimeField(_('Date de création'))
    last_connection = models.GenericIPAddressField(_('Dernière connexion'), protocol='both', unpack_ipv4=False, default=None, blank=True, null=True)

    def __str__(self):
        return str(self.created_date)

    def save(self, *args, **kwargs):
        self.baby.last_activity = timezone.now()
        self.baby.save()

        return super(Activity, self).save(*args, **kwargs)
    class Meta:
        verbose_name = _('Activité')
        verbose_name_plural = _('Activités')
        ordering = ['-created_date']

class BetaUser(models.Model):
    email = models.EmailField(_(u'Adresse email'), help_text=_("Veuillez saisir votre email pour vous inscrire à la beta"))
    signup_date = models.DateTimeField(_("Date d'inscription"), auto_now_add=True)

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        send_mail(
            'Nouvelle inscription',
            "Un•e nouvel•le utilisateur•trice vient de s'incrire " + self.email,
            'support@romy.baby',
            ['john@example.com', 'jane@example.com'],
        )

        return super(BetaUser, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Adresse email de la beta')
        verbose_name_plural = _('Adresses email de la beta')
