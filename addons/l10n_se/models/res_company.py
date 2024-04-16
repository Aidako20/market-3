#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models
importre


classResCompany(models.Model):
    _inherit='res.company'

    org_number=fields.Char(compute='_compute_org_number')

    @api.depends('vat')
    def_compute_org_number(self):
        forcompanyinself:
            ifcompany.country_id.code=="SE"andcompany.vat:
                org_number=re.sub(r'\D','',company.vat)[:-2]
                org_number=org_number[:6]+'-'+org_number[6:]

                company.org_number=org_number
            else:
                company.org_number=''
