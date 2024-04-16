#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classGamificationBadge(models.Model):
    _name='gamification.badge'
    _inherit=['gamification.badge','website.published.mixin']
