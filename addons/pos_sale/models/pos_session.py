#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classPosSession(models.Model):
    _inherit='pos.session'

    crm_team_id=fields.Many2one('crm.team',related='config_id.crm_team_id',string="SalesTeam",readonly=True)
