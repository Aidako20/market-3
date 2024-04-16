#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields


classChallenge(models.Model):
    _inherit='gamification.challenge'

    challenge_category=fields.Selection(selection_add=[
        ('forum','Website/Forum')
    ],ondelete={'forum':'setdefault'})
