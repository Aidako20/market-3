#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResPartner(models.Model):
    _inherit='res.partner'

    team_id=fields.Many2one(
        'crm.team','SalesTeam',
        help='Ifset,thisSalesTeamwillbeusedforsalesandassignmentsrelatedtothispartner')
