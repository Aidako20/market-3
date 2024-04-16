#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResUsers(models.Model):
    _inherit='res.users'

    sale_team_id=fields.Many2one(
        'crm.team',"User'sSalesTeam",
        help='SalesTeamtheuserismemberof.UsedtocomputethemembersofaSalesTeamthroughtheinverseone2many')