#-*-coding:utf-8-*-

fromflectraimportmodels,fields,api,_
fromflectra.toolsimportfloat_round
fromflectra.exceptionsimportValidationError


classAccountCashRounding(models.Model):
    """
    Insomecountries,weneedtobeabletomakeappearonaninvoicearoundingline,appearingthereonlybecausethe
    smallestcoinagehasbeenremovedfromthecirculation.Forexample,inSwitzerlandinvoiceshavetoberoundedto
    0.05CHFbecausecoinsof0.01CHFand0.02CHFaren'tusedanymore.
    seehttps://en.wikipedia.org/wiki/Cash_roundingformoredetails.
    """
    _name='account.cash.rounding'
    _description='AccountCashRounding'

    name=fields.Char(string='Name',translate=True,required=True)
    rounding=fields.Float(string='RoundingPrecision',required=True,default=0.01,
        help='Representthenon-zerovaluesmallestcoinage(forexample,0.05).')
    strategy=fields.Selection([('biggest_tax','Modifytaxamount'),('add_invoice_line','Addaroundingline')],
        string='RoundingStrategy',default='add_invoice_line',required=True,
        help='Specifywhichwaywillbeusedtoroundtheinvoiceamounttotheroundingprecision')
    profit_account_id=fields.Many2one('account.account',string='ProfitAccount',company_dependent=True,domain="[('deprecated','=',False),('company_id','=',current_company_id)]")
    loss_account_id=fields.Many2one('account.account',string='LossAccount',company_dependent=True,domain="[('deprecated','=',False),('company_id','=',current_company_id)]")
    rounding_method=fields.Selection(string='RoundingMethod',required=True,
        selection=[('UP','UP'),('DOWN','DOWN'),('HALF-UP','HALF-UP')],
        default='HALF-UP',help='Thetie-breakingruleusedforfloatroundingoperations')
    company_id=fields.Many2one('res.company',related='profit_account_id.company_id')

    @api.constrains('rounding')
    defvalidate_rounding(self):
        forrecordinself:
            ifrecord.rounding<=0:
                raiseValidationError(_("Pleasesetastrictlypositiveroundingvalue."))

    defround(self,amount):
        """Computetheroundingontheamountpassedasparameter.

        :paramamount:theamounttoround
        :return:theroundedamountdependingtheroundingvalueandtheroundingmethod
        """
        returnfloat_round(amount,precision_rounding=self.rounding,rounding_method=self.rounding_method)

    defcompute_difference(self,currency,amount):
        """Computethedifferencebetweenthebase_amountandtheamountafterrounding.
        Forexample,base_amount=23.91,afterrounding=24.00,theresultwillbe0.09.

        :paramcurrency:Thecurrency.
        :paramamount:Theamount
        :return:round(difference)
        """
        difference=self.round(amount)-amount
        returncurrency.round(difference)
