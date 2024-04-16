#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models
fromflectra.tools.sqlimportcolumn_exists,create_column


classProductTemplate(models.Model):
    _inherit="product.template"

    can_be_expensed=fields.Boolean(string="CanbeExpensed",compute='_compute_can_be_expensed',
        store=True,readonly=False,help="Specifywhethertheproductcanbeselectedinanexpense.")

    def_auto_init(self):
        ifnotcolumn_exists(self.env.cr,"product_template","can_be_expensed"):
            create_column(self.env.cr,"product_template","can_be_expensed","boolean")
            self.env.cr.execute(
                """
                UPDATEproduct_template
                SETcan_be_expensed=false
                WHEREtypeNOTIN('consu','service')
                """
            )
        returnsuper()._auto_init()

    @api.model
    defdefault_get(self,fields):
        result=super(ProductTemplate,self).default_get(fields)
        ifself.env.context.get('default_can_be_expensed'):
            result['supplier_taxes_id']=False
        returnresult

    @api.depends('type')
    def_compute_can_be_expensed(self):
        self.filtered(lambdap:p.typenotin['consu','service']).update({'can_be_expensed':False})
