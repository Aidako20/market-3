#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classUsers(models.Model):
    _inherit='res.users'

    target_sales_won=fields.Integer('WoninOpportunitiesTarget')
    target_sales_done=fields.Integer('ActivitiesDoneTarget')
