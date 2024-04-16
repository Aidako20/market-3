#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classCompany(models.Model):
    _inherit='res.company'

    street_name=fields.Char('StreetName',compute='_compute_address',
                              inverse='_inverse_street_name')
    street_number=fields.Char('HouseNumber',compute='_compute_address',
                                inverse='_inverse_street_number')
    street_number2=fields.Char('DoorNumber',compute='_compute_address',
                                 inverse='_inverse_street_number2')

    def_get_company_address_field_names(self):
        fields_matching=super(Company,self)._get_company_address_field_names()
        returnlist(set(fields_matching+['street_name','street_number','street_number2']))

    def_inverse_street_name(self):
        forcompanyinself:
            company.partner_id.street_name=company.street_name

    def_inverse_street_number(self):
        forcompanyinself:
            company.partner_id.street_number=company.street_number

    def_inverse_street_number2(self):
        forcompanyinself:
            company.partner_id.street_number2=company.street_number2
