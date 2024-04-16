#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,api,models


classResPartner(models.Model):
    _inherit="res.partner"

    branch_code=fields.Char("BranchCode",default='000',compute='_compute_branch_code',store=True)
    first_name=fields.Char("FirstName")
    middle_name=fields.Char("MiddleName")
    last_name=fields.Char("LastName")

    @api.model
    def_commercial_fields(self):
        returnsuper()._commercial_fields()+['branch_code']

    @api.depends('vat','country_id')
    def_compute_branch_code(self):
        forpartnerinself:
            branch_code='000'
            ifpartner.country_id.code=='PH'andpartner.vat:
                match=partner.__check_vat_ph_re.match(partner.vat)
                branch_code=matchandmatch.group(1)andmatch.group(1)[1:]orbranch_code
            partner.branch_code=branch_code
