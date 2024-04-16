#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    group_mass_mailing_campaign=fields.Boolean(string="MailingCampaigns",implied_group='mass_mailing.group_mass_mailing_campaign',help="""Thisisusefulifyourmarketingcampaignsarecomposedofseveralemails""")
    mass_mailing_outgoing_mail_server=fields.Boolean(string="DedicatedServer",config_parameter='mass_mailing.outgoing_mail_server',
        help='Useaspecificmailserverinpriority.OtherwiseFlectrareliesonthefirstoutgoingmailserveravailable(basedontheirsequencing)asitdoesfornormalmails.')
    mass_mailing_mail_server_id=fields.Many2one('ir.mail_server',string='MailServer',config_parameter='mass_mailing.mail_server_id')
    show_blacklist_buttons=fields.Boolean(string="BlacklistOptionwhenUnsubscribing",
                                                 config_parameter='mass_mailing.show_blacklist_buttons',
                                                 help="""Allowtherecipienttomanagehimselfhisstateintheblacklistviatheunsubscriptionpage.""")

    @api.onchange('mass_mailing_outgoing_mail_server')
    def_onchange_mass_mailing_outgoing_mail_server(self):
        ifnotself.mass_mailing_outgoing_mail_server:
            self.mass_mailing_mail_server_id=False
