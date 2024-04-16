#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels
fromstdnumimportluhn


classAccountMove(models.Model):
    _inherit="account.move"

    def_get_invoice_reference_no_invoice(self):
        """ThiscomputesthereferencebasedontheFlectraformat.
            Wecalculatreferenceusinginvoicenumberand
            partneridandaddedcontroldigitatlast.
        """
        returnself._get_kid_number()

    def_get_invoice_reference_no_partner(self):
        """ThiscomputesthereferencebasedontheFlectraformat.
            Wecalculatreferenceusinginvoicenumberand
            partneridandaddedcontroldigitatlast.
        """
        returnself._get_kid_number()

    def_get_kid_number(self):
        self.ensure_one()
        invoice_name=''.join([iforiinself.nameifi.isdigit()]).zfill(7)
        ref=(str(self.partner_id.id).zfill(7)[-7:]+invoice_name[-7:])
        returnref+luhn.calc_check_digit(ref)
