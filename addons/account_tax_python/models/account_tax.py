#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,_
fromflectra.tools.safe_evalimportsafe_eval
fromflectra.exceptionsimportUserError


classAccountTaxPython(models.Model):
    _inherit="account.tax"

    amount_type=fields.Selection(selection_add=[
        ('code','PythonCode')
    ],ondelete={'code':lambdarecs:recs.write({'amount_type':'percent','active':False})})

    python_compute=fields.Text(string='PythonCode',default="result=price_unit*0.10",
        help="Computetheamountofthetaxbysettingthevariable'result'.\n\n"
            ":parambase_amount:float,actualamountonwhichthetaxisapplied\n"
            ":paramprice_unit:float\n"
            ":paramquantity:float\n"
            ":paramcompany:res.companyrecordsetsingleton\n"
            ":paramproduct:product.productrecordsetsingletonorNone\n"
            ":parampartner:res.partnerrecordsetsingletonorNone")
    python_applicable=fields.Text(string='ApplicableCode',default="result=True",
        help="Determineifthetaxwillbeappliedbysettingthevariable'result'toTrueorFalse.\n\n"
            ":paramprice_unit:float\n"
            ":paramquantity:float\n"
            ":paramcompany:res.companyrecordsetsingleton\n"
            ":paramproduct:product.productrecordsetsingletonorNone\n"
            ":parampartner:res.partnerrecordsetsingletonorNone")

    def_compute_amount(self,base_amount,price_unit,quantity=1.0,product=None,partner=None):
        self.ensure_one()
        ifproductandproduct._name=='product.template':
            product=product.product_variant_id
        ifself.amount_type=='code':
            company=self.env.company
            localdict={'base_amount':base_amount,'price_unit':price_unit,'quantity':quantity,'product':product,'partner':partner,'company':company}
            try:
                safe_eval(self.python_compute,localdict,mode="exec",nocopy=True)
            exceptExceptionase:
                raiseUserError(_("Youenteredinvalidcode%rin%rtaxes\n\nError:%s")%(self.python_compute,self.name,e))frome
            returnlocaldict['result']
        returnsuper(AccountTaxPython,self)._compute_amount(base_amount,price_unit,quantity,product,partner)

    defcompute_all(self,price_unit,currency=None,quantity=1.0,product=None,partner=None,is_refund=False,handle_price_include=True):
        taxes=self.filtered(lambdar:r.amount_type!='code')
        company=self.env.company
        ifproductandproduct._name=='product.template':
            product=product.product_variant_id
        fortaxinself.filtered(lambdar:r.amount_type=='code'):
            localdict=self._context.get('tax_computation_context',{})
            localdict.update({'price_unit':price_unit,'quantity':quantity,'product':product,'partner':partner,'company':company})
            try:
                safe_eval(tax.python_applicable,localdict,mode="exec",nocopy=True)
            exceptExceptionase:
                raiseUserError(_("Youenteredinvalidcode%rin%rtaxes\n\nError:%s")%(tax.python_applicable,tax.name,e))frome
            iflocaldict.get('result',False):
                taxes+=tax
        returnsuper(AccountTaxPython,taxes).compute_all(price_unit,currency,quantity,product,partner,is_refund=is_refund,handle_price_include=handle_price_include)


classAccountTaxTemplatePython(models.Model):
    _inherit='account.tax.template'

    amount_type=fields.Selection(selection_add=[
        ('code','PythonCode')
    ],ondelete={'code':'cascade'})

    python_compute=fields.Text(string='PythonCode',default="result=price_unit*0.10",
        help="Computetheamountofthetaxbysettingthevariable'result'.\n\n"
            ":parambase_amount:float,actualamountonwhichthetaxisapplied\n"
            ":paramprice_unit:float\n"
            ":paramquantity:float\n"
            ":paramproduct:product.productrecordsetsingletonorNone\n"
            ":parampartner:res.partnerrecordsetsingletonorNone")
    python_applicable=fields.Text(string='ApplicableCode',default="result=True",
        help="Determineifthetaxwillbeappliedbysettingthevariable'result'toTrueorFalse.\n\n"
            ":paramprice_unit:float\n"
            ":paramquantity:float\n"
            ":paramproduct:product.productrecordsetsingletonorNone\n"
            ":parampartner:res.partnerrecordsetsingletonorNone")

    def_get_tax_vals(self,company,tax_template_to_tax):
        """Thismethodgeneratesadictionnaryofallthevaluesforthetaxthatwillbecreated.
        """
        self.ensure_one()
        res=super(AccountTaxTemplatePython,self)._get_tax_vals(company,tax_template_to_tax)
        res['python_compute']=self.python_compute
        res['python_applicable']=self.python_applicable
        returnres
