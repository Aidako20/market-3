#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportmodels
fromflectra.toolsimportfloat_repr


classAccountMove(models.Model):
    _inherit='account.move'

    def_get_ubl_values(self):
        self.ensure_one()

        defformat_monetary(amount):
            #Formatthemonetaryvaluestoavoidtrailingdecimals(e.g.90.85000000000001).
            returnfloat_repr(amount,self.currency_id.decimal_places)

        return{
            'invoice':self,
            'ubl_version':2.1,
            'type_code':380ifself.move_type=='out_invoice'else381,
            'payment_means_code':42ifself.journal_id.bank_account_idelse31,
            'format_monetary':format_monetary,
        }
