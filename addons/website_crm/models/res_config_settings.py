#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    def_get_crm_default_team_domain(self):
        ifnotself.env.user.has_group('crm.group_use_lead'):
            return[('use_opportunities','=',True)]
        return[('use_leads','=',True)]

    crm_default_team_id=fields.Many2one(
        'crm.team',string='DefaultSalesTeam',related='website_id.crm_default_team_id',readonly=False,
        domain=lambdaself:self._get_crm_default_team_domain(),
        help='DefaultSalesTeamfornewleadscreatedthroughtheContactUsform.')
    crm_default_user_id=fields.Many2one(
        'res.users',string='DefaultSalesperson',related='website_id.crm_default_user_id',domain=[('share','=',False)],readonly=False,
        help='DefaultsalespersonfornewleadscreatedthroughtheContactUsform.')
