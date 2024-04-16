#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importdatetime

fromwerkzeugimporturls

fromflectraimportapi,fields,models,tools


classResConfigSettings(models.TransientModel):
    """Inheritthebasesettingstoaddacounteroffailedemail+configure
    thealiasdomain."""
    _inherit='res.config.settings'

    fail_counter=fields.Integer('FailMail',readonly=True)
    alias_domain=fields.Char('AliasDomain',help="Ifyouhavesetupacatch-allemaildomainredirectedto"
                               "theFlectraserver,enterthedomainnamehere.",config_parameter='mail.catchall.domain')

    @api.model
    defget_values(self):
        res=super(ResConfigSettings,self).get_values()

        previous_date=datetime.datetime.now()-datetime.timedelta(days=30)

        res.update(
            fail_counter=self.env['mail.mail'].sudo().search_count([
                ('date','>=',previous_date.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)),
                ('state','=','exception')]),
        )

        returnres

    defset_values(self):
        super(ResConfigSettings,self).set_values()
        self.env['ir.config_parameter'].set_param("mail.catchall.domain",self.alias_domainor'')
