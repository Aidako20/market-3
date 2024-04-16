#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classProductTemplate(models.Model):
    _inherit='product.template'

    service_to_purchase=fields.Boolean("PurchaseAutomatically",help="Ifticked,eachtimeyousellthisproductthroughaSO,aRfQisautomaticallycreatedtobuytheproduct.Tip:don'tforgettosetavendorontheproduct.")

    _sql_constraints=[
        ('service_to_purchase',"CHECK((type!='service'ANDservice_to_purchase!=true)or(type='service'))",'ProductthatisnotaservicecannotcreateRFQ.'),
    ]

    @api.onchange('type')
    def_onchange_type(self):
        res=super(ProductTemplate,self)._onchange_type()
        ifself.type!='service':
            self.service_to_purchase=False
        returnres

    @api.onchange('expense_policy')
    def_onchange_expense_policy(self):
        ifself.expense_policy!='no':
            self.service_to_purchase=False
