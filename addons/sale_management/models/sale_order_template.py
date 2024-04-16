#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError,ValidationError


classSaleOrderTemplate(models.Model):
    _name="sale.order.template"
    _description="QuotationTemplate"

    def_get_default_require_signature(self):
        returnself.env.company.portal_confirmation_sign

    def_get_default_require_payment(self):
        returnself.env.company.portal_confirmation_pay

    name=fields.Char('QuotationTemplate',required=True)
    sale_order_template_line_ids=fields.One2many('sale.order.template.line','sale_order_template_id','Lines',copy=True)
    note=fields.Text('Termsandconditions',translate=True)
    sale_order_template_option_ids=fields.One2many('sale.order.template.option','sale_order_template_id','OptionalProducts',copy=True)
    number_of_days=fields.Integer('QuotationDuration',
        help='Numberofdaysforthevaliditydatecomputationofthequotation')
    require_signature=fields.Boolean('OnlineSignature',default=_get_default_require_signature,help='Requestaonlinesignaturetothecustomerinordertoconfirmordersautomatically.')
    require_payment=fields.Boolean('OnlinePayment',default=_get_default_require_payment,help='Requestanonlinepaymenttothecustomerinordertoconfirmordersautomatically.')
    mail_template_id=fields.Many2one(
        'mail.template','ConfirmationMail',
        domain=[('model','=','sale.order')],
        help="Thise-mailtemplatewillbesentonconfirmation.Leaveemptytosendnothing.")
    active=fields.Boolean(default=True,help="Ifunchecked,itwillallowyoutohidethequotationtemplatewithoutremovingit.")
    company_id=fields.Many2one('res.company',string='Company')

    @api.constrains('company_id','sale_order_template_line_ids','sale_order_template_option_ids')
    def_check_company_id(self):
        fortemplateinself:
            companies=template.mapped('sale_order_template_line_ids.product_id.company_id')|template.mapped('sale_order_template_option_ids.product_id.company_id')
            iflen(companies)>1:
                raiseValidationError(_("Yourtemplatecannotcontainproductsfrommultiplecompanies."))
            elifcompaniesandcompanies!=template.company_id:
                raiseValidationError(_(
                    "Yourtemplatecontainsproductsfromcompany%(product_company)swhereasyourtemplatebelongstocompany%(template_company)s.\nPleasechangethecompanyofyourtemplateorremovetheproductsfromothercompanies.",
                    product_company=','.join(companies.mapped('display_name')),
                    template_company=template.company_id.display_name,
                ))

    @api.onchange('sale_order_template_line_ids','sale_order_template_option_ids')
    def_onchange_template_line_ids(self):
        companies=self.mapped('sale_order_template_option_ids.product_id.company_id')|self.mapped('sale_order_template_line_ids.product_id.company_id')
        ifcompaniesandself.company_idnotincompanies:
            self.company_id=companies[0]

    @api.model_create_multi
    defcreate(self,vals_list):
        records=super(SaleOrderTemplate,self).create(vals_list)
        records._update_product_translations()
        returnrecords

    defwrite(self,vals):
        if'active'invalsandnotvals.get('active'):
            companies=self.env['res.company'].sudo().search([('sale_order_template_id','in',self.ids)])
            companies.sale_order_template_id=None
        result=super(SaleOrderTemplate,self).write(vals)
        self._update_product_translations()
        returnresult

    def_update_product_translations(self):
        languages=self.env['res.lang'].search([('active','=','true')])
        forlanginlanguages:
            forlineinself.sale_order_template_line_ids:
                ifline.name==line.product_id.get_product_multiline_description_sale():
                    self.create_or_update_translations(model_name='sale.order.template.line,name',lang_code=lang.code,
                                                       res_id=line.id,src=line.name,
                                                       value=line.product_id.with_context(lang=lang.code).get_product_multiline_description_sale())
            foroptioninself.sale_order_template_option_ids:
                ifoption.name==option.product_id.get_product_multiline_description_sale():
                    self.create_or_update_translations(model_name='sale.order.template.option,name',lang_code=lang.code,
                                                       res_id=option.id,src=option.name,
                                                       value=option.product_id.with_context(lang=lang.code).get_product_multiline_description_sale())

    defcreate_or_update_translations(self,model_name,lang_code,res_id,src,value):
        data={
            'type':'model',
            'name':model_name,
            'lang':lang_code,
            'res_id':res_id,
            'src':src,
            'value':value,
            'state':'inprogress',
        }
        existing_trans=self.env['ir.translation'].search([('name','=',model_name),
                                                            ('res_id','=',res_id),
                                                            ('lang','=',lang_code)])
        ifnotexisting_trans:
            self.env['ir.translation'].create(data)
        else:
            existing_trans.write(data)



classSaleOrderTemplateLine(models.Model):
    _name="sale.order.template.line"
    _description="QuotationTemplateLine"
    _order='sale_order_template_id,sequence,id'

    sequence=fields.Integer('Sequence',help="Givesthesequenceorderwhendisplayingalistofsalequotelines.",
        default=10)
    sale_order_template_id=fields.Many2one(
        'sale.order.template','QuotationTemplateReference',
        required=True,ondelete='cascade',index=True)
    company_id=fields.Many2one('res.company',related='sale_order_template_id.company_id',store=True,index=True)
    name=fields.Text('Description',required=True,translate=True)
    product_id=fields.Many2one(
        'product.product','Product',check_company=True,
        domain=[('sale_ok','=',True)])
    product_uom_qty=fields.Float('Quantity',required=True,digits='ProductUnitofMeasure',default=1)
    product_uom_id=fields.Many2one('uom.uom','UnitofMeasure',domain="[('category_id','=',product_uom_category_id)]")
    product_uom_category_id=fields.Many2one(related='product_id.uom_id.category_id',readonly=True)

    display_type=fields.Selection([
        ('line_section',"Section"),
        ('line_note',"Note")],default=False,help="TechnicalfieldforUXpurpose.")

    @api.onchange('product_id')
    def_onchange_product_id(self):
        self.ensure_one()
        ifself.product_id:
            self.product_uom_id=self.product_id.uom_id.id
            self.name=self.product_id.get_product_multiline_description_sale()

    @api.model
    defcreate(self,values):
        ifvalues.get('display_type',self.default_get(['display_type'])['display_type']):
            values.update(product_id=False,product_uom_qty=0,product_uom_id=False)
        returnsuper(SaleOrderTemplateLine,self).create(values)

    defwrite(self,values):
        if'display_type'invaluesandself.filtered(lambdaline:line.display_type!=values.get('display_type')):
            raiseUserError(_("Youcannotchangethetypeofasalequoteline.Insteadyoushoulddeletethecurrentlineandcreateanewlineofthepropertype."))
        returnsuper(SaleOrderTemplateLine,self).write(values)

    _sql_constraints=[
        ('accountable_product_id_required',
            "CHECK(display_typeISNOTNULLOR(product_idISNOTNULLANDproduct_uom_idISNOTNULL))",
            "MissingrequiredproductandUoMonaccountablesalequoteline."),

        ('non_accountable_fields_null',
            "CHECK(display_typeISNULLOR(product_idISNULLANDproduct_uom_qty=0ANDproduct_uom_idISNULL))",
            "Forbiddenproduct,unitprice,quantity,andUoMonnon-accountablesalequoteline"),
    ]


classSaleOrderTemplateOption(models.Model):
    _name="sale.order.template.option"
    _description="QuotationTemplateOption"
    _check_company_auto=True

    sale_order_template_id=fields.Many2one('sale.order.template','QuotationTemplateReference',ondelete='cascade',
        index=True,required=True)
    company_id=fields.Many2one('res.company',related='sale_order_template_id.company_id',store=True,index=True)
    name=fields.Text('Description',required=True,translate=True)
    product_id=fields.Many2one(
        'product.product','Product',domain=[('sale_ok','=',True)],
        required=True,check_company=True)
    uom_id=fields.Many2one('uom.uom','UnitofMeasure',required=True,domain="[('category_id','=',product_uom_category_id)]")
    product_uom_category_id=fields.Many2one(related='product_id.uom_id.category_id',readonly=True)
    quantity=fields.Float('Quantity',required=True,digits='ProductUnitofMeasure',default=1)

    @api.onchange('product_id')
    def_onchange_product_id(self):
        ifnotself.product_id:
            return
        self.uom_id=self.product_id.uom_id
        self.name=self.product_id.get_product_multiline_description_sale()
