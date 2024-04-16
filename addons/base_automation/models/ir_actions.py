#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classServerAction(models.Model):
    _inherit="ir.actions.server"

    usage=fields.Selection(selection_add=[
        ('base_automation','AutomatedAction')
    ],ondelete={'base_automation':'cascade'})
