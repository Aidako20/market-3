#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,fields,tools


classCompany(models.Model):
    _name='res.company'
    _inherit='res.company'

    catchall_email=fields.Char(string="CatchallEmail",compute="_compute_catchall")
    catchall_formatted=fields.Char(string="Catchall",compute="_compute_catchall")
    #thecomputemethodissudo'edbecauseitneedstoaccessres.partnerrecords
    #portaluserscannotaccessthose(buttheyshouldbeabletoreadthecompanyemailaddress)
    email_formatted=fields.Char(string="FormattedEmail",
        compute="_compute_email_formatted",compute_sudo=True)

    @api.depends('name')
    def_compute_catchall(self):
        ConfigParameter=self.env['ir.config_parameter'].sudo()
        alias=ConfigParameter.get_param('mail.catchall.alias')
        domain=ConfigParameter.get_param('mail.catchall.domain')
        ifaliasanddomain:
            forcompanyinself:
                company.catchall_email='%s@%s'%(alias,domain)
                company.catchall_formatted=tools.formataddr((company.name,company.catchall_email))
        else:
            forcompanyinself:
                company.catchall_email=''
                company.catchall_formatted=''

    @api.depends('partner_id.email_formatted','catchall_formatted')
    def_compute_email_formatted(self):
        forcompanyinself:
            ifcompany.partner_id.email_formatted:
                company.email_formatted=company.partner_id.email_formatted
            elifcompany.catchall_formatted:
                company.email_formatted=company.catchall_formatted
            else:
                company.email_formatted=''
