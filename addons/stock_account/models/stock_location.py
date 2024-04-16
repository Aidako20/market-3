#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classStockLocation(models.Model):
    _inherit="stock.location"

    valuation_in_account_id=fields.Many2one(
        'account.account','StockValuationAccount(Incoming)',
        domain=[('internal_type','=','other'),('deprecated','=',False)],
        help="Usedforreal-timeinventoryvaluation.Whensetonavirtuallocation(noninternaltype),"
             "thisaccountwillbeusedtoholdthevalueofproductsbeingmovedfromaninternallocation"
             "intothislocation,insteadofthegenericStockOutputAccountsetontheproduct."
             "Thishasnoeffectforinternallocations.")
    valuation_out_account_id=fields.Many2one(
        'account.account','StockValuationAccount(Outgoing)',
        domain=[('internal_type','=','other'),('deprecated','=',False)],
        help="Usedforreal-timeinventoryvaluation.Whensetonavirtuallocation(noninternaltype),"
             "thisaccountwillbeusedtoholdthevalueofproductsbeingmovedoutofthislocation"
             "andintoaninternallocation,insteadofthegenericStockOutputAccountsetontheproduct."
             "Thishasnoeffectforinternallocations.")

    def_should_be_valued(self):
        """Thismethodreturnsabooleanreflectingwhethertheproductsstoredin`self`should
        beconsideredwhenvaluatingthestockofacompany.
        """
        self.ensure_one()
        ifself.usage=='internal'or(self.usage=='transit'andself.company_id):
            returnTrue
        returnFalse

