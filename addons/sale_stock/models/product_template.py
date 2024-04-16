#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classProductTemplate(models.Model):
    _inherit='product.template'

    @api.onchange('type')
    def_onchange_type(self):
        """Wewanttopreventstorableproducttobeexpensed,sinceitmakenosenseaswhenconfirm
            expenses,theproductisalreadyoutofourstock.
        """
        res=super(ProductTemplate,self)._onchange_type()
        ifself.type=='product':
            self.expense_policy='no'
            self.service_type='manual'
        returnres
