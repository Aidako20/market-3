#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResCompany(models.Model):
    _inherit="res.company"

    ldaps=fields.One2many('res.company.ldap','company',string='LDAPParameters',
                               copy=True,groups="base.group_system")
