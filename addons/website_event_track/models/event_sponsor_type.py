#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classSponsorType(models.Model):
    _name="event.sponsor.type"
    _description='EventSponsorType'
    _order="sequence"

    name=fields.Char('SponsorType',required=True,translate=True)
    sequence=fields.Integer('Sequence')
    display_ribbon_style=fields.Selection([
        ('no_ribbon','NoRibbon'),
        ('Gold','Gold'),
        ('Silver','Silver'),
        ('Bronze','Bronze')],string='RibbonStyle')
