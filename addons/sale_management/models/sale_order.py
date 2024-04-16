#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimporttimedelta

fromflectraimportapi,fields,models,_,SUPERUSER_ID
fromflectra.exceptionsimportUserError,ValidationError


classSaleOrder(models.Model):
    _inherit='sale.order'

    @api.model
    defdefault_get(self,fields_list):
        default_vals=super(SaleOrder,self).default_get(fields_list)
        if"sale_order_template_id"infields_listandnotdefault_vals.get("sale_order_template_id"):
            company_id=default_vals.get('company_id',False)
            company=self.env["res.company"].browse(company_id)ifcompany_idelseself.env.company
            default_vals['sale_order_template_id']=company.sale_order_template_id.id
        returndefault_vals

    sale_order_template_id=fields.Many2one(
        'sale.order.template','QuotationTemplate',
        readonly=True,check_company=True,
        states={'draft':[('readonly',False)],'sent':[('readonly',False)]},
        domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    sale_order_option_ids=fields.One2many(
        'sale.order.option','order_id','OptionalProductsLines',
        copy=True,readonly=True,
        states={'draft':[('readonly',False)],'sent':[('readonly',False)]})

    @api.constrains('company_id','sale_order_option_ids')
    def_check_optional_product_company_id(self):
        fororderinself:
            companies=order.sale_order_option_ids.product_id.company_id
            ifcompaniesandcompanies!=order.company_id:
                bad_products=order.sale_order_option_ids.product_id.filtered(lambdap:p.company_idandp.company_id!=order.company_id)
                raiseValidationError(_(
                    "Yourquotationcontainsproductsfromcompany%(product_company)swhereasyourquotationbelongstocompany%(quote_company)s.\nPleasechangethecompanyofyourquotationorremovetheproductsfromothercompanies(%(bad_products)s).",
                    product_company=','.join(companies.mapped('display_name')),
                    quote_company=order.company_id.display_name,
                    bad_products=','.join(bad_products.mapped('display_name')),
                ))

    @api.returns('self',lambdavalue:value.id)
    defcopy(self,default=None):
        ifself.sale_order_template_idandself.sale_order_template_id.number_of_days>0:
            default=dict(defaultor{})
            default['validity_date']=fields.Date.context_today(self)+timedelta(self.sale_order_template_id.number_of_days)
        returnsuper(SaleOrder,self).copy(default=default)

    @api.onchange('partner_id')
    defonchange_partner_id(self):
        super(SaleOrder,self).onchange_partner_id()
        template=self.sale_order_template_id.with_context(lang=self.partner_id.lang)
        self.note=template.noteorself.note

    def_compute_line_data_for_template_change(self,line):
        return{
            'display_type':line.display_type,
            'name':line.name,
            'state':'draft',
        }

    def_compute_option_data_for_template_change(self,option):
        price=option.product_id.lst_price
        discount=0

        ifself.pricelist_id:
            pricelist_price=self.pricelist_id.with_context(uom=option.uom_id.id).get_product_price(option.product_id,1,False)

            ifself.pricelist_id.discount_policy=='without_discount'andprice:
                discount=max(0,(price-pricelist_price)*100/price)
            else:
                price=pricelist_price

        return{
            'product_id':option.product_id.id,
            'name':option.name,
            'quantity':option.quantity,
            'uom_id':option.uom_id.id,
            'price_unit':price,
            'discount':discount
        }

    defupdate_prices(self):
        self.ensure_one()
        res=super().update_prices()
        self.sale_order_option_ids._update_price_and_discount()
        returnres

    @api.onchange('sale_order_template_id')
    defonchange_sale_order_template_id(self):

        ifnotself.sale_order_template_id:
            self.require_signature=self._get_default_require_signature()
            self.require_payment=self._get_default_require_payment()
            return

        template=self.sale_order_template_id.with_context(lang=self.partner_id.lang)

        #---first,processthelistofproductsfromthetemplate
        order_lines=[(5,0,0)]
        forlineintemplate.sale_order_template_line_ids:
            data=self._compute_line_data_for_template_change(line)

            ifline.product_id:
                price=line.product_id.lst_price
                discount=0

                ifself.pricelist_id:
                    pricelist_price=self.pricelist_id.with_context(uom=line.product_uom_id.id).get_product_price(line.product_id,1,False)

                    ifself.pricelist_id.discount_policy=='without_discount'andprice:
                        discount=max(0,(price-pricelist_price)*100/price)
                    else:
                        price=pricelist_price

                data.update({
                    'price_unit':price,
                    'discount':discount,
                    'product_uom_qty':line.product_uom_qty,
                    'product_id':line.product_id.id,
                    'product_uom':line.product_uom_id.id,
                    'customer_lead':self._get_customer_lead(line.product_id.product_tmpl_id),
                })

            order_lines.append((0,0,data))

        self.order_line=order_lines
        self.order_line._compute_tax_id()

        #then,processthelistofoptionalproductsfromthetemplate
        option_lines=[(5,0,0)]
        foroptionintemplate.sale_order_template_option_ids:
            data=self._compute_option_data_for_template_change(option)
            option_lines.append((0,0,data))

        self.sale_order_option_ids=option_lines

        iftemplate.number_of_days>0:
            self.validity_date=fields.Date.context_today(self)+timedelta(template.number_of_days)

        self.require_signature=template.require_signature
        self.require_payment=template.require_payment

        iftemplate.note:
            self.note=template.note

    defaction_confirm(self):
        res=super(SaleOrder,self).action_confirm()
        ifself.env.su:
            self=self.with_user(SUPERUSER_ID)

        fororderinself:
            iforder.sale_order_template_idandorder.sale_order_template_id.mail_template_id:
                order.sale_order_template_id.mail_template_id.send_mail(order.id)
        returnres

    defget_access_action(self,access_uid=None):
        """Insteadoftheclassicformview,redirecttotheonlinequoteifitexists."""
        self.ensure_one()
        user=access_uidandself.env['res.users'].sudo().browse(access_uid)orself.env.user

        ifnotself.sale_order_template_idor(notuser.shareandnotself.env.context.get('force_website')):
            returnsuper(SaleOrder,self).get_access_action(access_uid)
        return{
            'type':'ir.actions.act_url',
            'url':self.get_portal_url(),
            'target':'self',
            'res_id':self.id,
        }


classSaleOrderLine(models.Model):
    _inherit="sale.order.line"
    _description="SalesOrderLine"

    sale_order_option_ids=fields.One2many('sale.order.option','line_id','OptionalProductsLines')

    #Takethedescriptionontheordertemplateiftheproductispresentinit
    @api.onchange('product_id')
    defproduct_id_change(self):
        domain=super(SaleOrderLine,self).product_id_change()
        ifself.product_idandself.order_id.sale_order_template_id:
            forlineinself.order_id.sale_order_template_id.sale_order_template_line_ids:
                ifline.product_id==self.product_id:
                    lang=self.order_id.partner_id.lang
                    self.name=line.with_context(lang=lang).name+self.with_context(lang=lang)._get_sale_order_line_multiline_description_variants()
                    break
        returndomain


classSaleOrderOption(models.Model):
    _name="sale.order.option"
    _description="SaleOptions"
    _order='sequence,id'

    is_present=fields.Boolean(string="PresentonQuotation",
                           help="Thisfieldwillbecheckediftheoptionline'sproductis"
                                "alreadypresentinthequotation.",
                           compute="_compute_is_present",search="_search_is_present")
    order_id=fields.Many2one('sale.order','SalesOrderReference',ondelete='cascade',index=True)
    line_id=fields.Many2one('sale.order.line',ondelete="setnull",copy=False)
    name=fields.Text('Description',required=True)
    product_id=fields.Many2one('product.product','Product',required=True,domain=[('sale_ok','=',True)])
    price_unit=fields.Float('UnitPrice',required=True,digits='ProductPrice')
    discount=fields.Float('Discount(%)',digits='Discount')
    uom_id=fields.Many2one('uom.uom','UnitofMeasure',required=True,domain="[('category_id','=',product_uom_category_id)]")
    product_uom_category_id=fields.Many2one(related='product_id.uom_id.category_id',readonly=True)
    quantity=fields.Float('Quantity',required=True,digits='ProductUnitofMeasure',default=1)
    sequence=fields.Integer('Sequence',help="Givesthesequenceorderwhendisplayingalistofoptionalproducts.")

    def_update_price_and_discount(self):
        foroptioninself:
            ifnotoption.product_id:
                continue
            #Tocomputethediscountasolineiscreatedincache
            values=option._get_values_to_add_to_order()
            new_sol=option.env['sale.order.line'].new(values)
            new_sol._onchange_discount()
            option.discount=new_sol.discount
            ifoption.order_id.pricelist_idandoption.order_id.partner_id:
                product=option.product_id.with_context(
                    partner=option.order_id.partner_id,
                    quantity=option.quantity,
                    date=option.order_id.date_order,
                    pricelist=option.order_id.pricelist_id.id,
                    uom=option.uom_id.id,
                    fiscal_position=option.env.context.get('fiscal_position')
                )
                option.price_unit=new_sol._get_display_price(product)

    @api.depends('line_id','order_id.order_line','product_id')
    def_compute_is_present(self):
        #NOTE:thisfieldcannotbestoredastheline_idisusuallyremoved
        #throughcascadedeletion,whichmeansthecomputewouldbefalse
        foroptioninself:
            option.is_present=bool(option.order_id.order_line.filtered(lambdal:l.product_id==option.product_id))

    def_search_is_present(self,operator,value):
        if(operator,value)in[('=',True),('!=',False)]:
            return[('line_id','=',False)]
        return[('line_id','!=',False)]

    @api.onchange('product_id','uom_id','quantity')
    def_onchange_product_id(self):
        ifnotself.product_id:
            return
        product=self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
        )
        self.uom_id=self.uom_idorproduct.uom_id
        self.name=product.get_product_multiline_description_sale()
        self._update_price_and_discount()

    defbutton_add_to_order(self):
        self.add_option_to_order()

    defadd_option_to_order(self):
        self.ensure_one()

        sale_order=self.order_id

        ifsale_order.statenotin['draft','sent']:
            raiseUserError(_('Youcannotaddoptionstoaconfirmedorder.'))

        values=self._get_values_to_add_to_order()
        order_line=self.env['sale.order.line'].create(values)
        order_line._compute_tax_id()

        self.write({'line_id':order_line.id})
        ifsale_order:
            sale_order.add_option_to_order_with_taxcloud()


    def_get_values_to_add_to_order(self):
        self.ensure_one()
        return{
            'order_id':self.order_id.id,
            'price_unit':self.price_unit,
            'name':self.name,
            'product_id':self.product_id.id,
            'product_uom_qty':self.quantity,
            'product_uom':self.uom_id.id,
            'discount':self.discount,
            'company_id':self.order_id.company_id.id,
        }
