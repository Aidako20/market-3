#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importlogging
importrandom
fromdatetimeimportdatetime
fromdateutil.relativedeltaimportrelativedelta

fromflectraimportapi,models,fields,_
fromflectra.httpimportrequest
fromflectra.osvimportexpression
fromflectra.exceptionsimportUserError,ValidationError

_logger=logging.getLogger(__name__)


classSaleOrder(models.Model):
    _inherit="sale.order"

    website_order_line=fields.One2many(
        'sale.order.line',
        compute='_compute_website_order_line',
        string='OrderLinesdisplayedonWebsite',
        help='OrderLinestobedisplayedonthewebsite.Theyshouldnotbeusedforcomputationpurpose.',
    )
    cart_quantity=fields.Integer(compute='_compute_cart_info',string='CartQuantity')
    only_services=fields.Boolean(compute='_compute_cart_info',string='OnlyServices')
    is_abandoned_cart=fields.Boolean('AbandonedCart',compute='_compute_abandoned_cart',search='_search_abandoned_cart')
    cart_recovery_email_sent=fields.Boolean('Cartrecoveryemailalreadysent')
    website_id=fields.Many2one('website',string='Website',readonly=True,
                                 help='Websitethroughwhichthisorderwasplaced.')

    @api.depends('order_line')
    def_compute_website_order_line(self):
        fororderinself:
            order.website_order_line=order.order_line

    @api.depends('order_line.product_uom_qty','order_line.product_id')
    def_compute_cart_info(self):
        fororderinself:
            order.cart_quantity=int(sum(order.mapped('website_order_line.product_uom_qty')))
            order.only_services=all(l.product_id.typein('service','digital')forlinorder.website_order_line)

    @api.depends('website_id','date_order','order_line','state','partner_id')
    def_compute_abandoned_cart(self):
        fororderinself:
            #aquotationcanbeconsideredasanabandonnedcartifitislinkedtoawebsite,
            #isinthe'draft'stateandhasanexpirationdate
            iforder.website_idandorder.state=='draft'andorder.date_order:
                public_partner_id=order.website_id.user_id.partner_id
                #bydefaulttheexpirationdateis1hourifnotspecifiedonthewebsiteconfiguration
                abandoned_delay=order.website_id.cart_abandoned_delayor1.0
                abandoned_datetime=datetime.utcnow()-relativedelta(hours=abandoned_delay)
                order.is_abandoned_cart=bool(order.date_order<=abandoned_datetimeandorder.partner_id!=public_partner_idandorder.order_line)
            else:
                order.is_abandoned_cart=False

    @api.onchange('partner_id')
    defonchange_partner_id(self):
        super().onchange_partner_id()
        fororderinself:
            iforder.website_id:
                order.payment_term_id=order.website_id.with_company(order.company_id).sale_get_payment_term(order.partner_id)

    def_search_abandoned_cart(self,operator,value):
        abandoned_delay=self.website_idandself.website_id.cart_abandoned_delayor1.0
        abandoned_datetime=fields.Datetime.to_string(datetime.utcnow()-relativedelta(hours=abandoned_delay))
        abandoned_domain=expression.normalize_domain([
            ('date_order','<=',abandoned_datetime),
            ('website_id','!=',False),
            ('state','=','draft'),
            ('partner_id','!=',self.env.ref('base.public_partner').id),
            ('order_line','!=',False)
        ])
        #is_abandoneddomainpossibilities
        if(operatornotinexpression.NEGATIVE_TERM_OPERATORSandvalue)or(operatorinexpression.NEGATIVE_TERM_OPERATORSandnotvalue):
            returnabandoned_domain
        returnexpression.distribute_not(['!']+abandoned_domain) #negativedomain

    def_cart_find_product_line(self,product_id=None,line_id=None,**kwargs):
        """Findthecartlinematchingthegivenparameters.

        Ifaproduct_idisgiven,thelinewillmatchtheproductonlyifthe
        linealsohasthesamespecialattributes:`no_variant`attributesand
        `is_custom`values.
        """
        self.ensure_one()
        product=self.env['product.product'].browse(product_id)

        #splitlineswiththesameproductifithasuntrackedattributes
        ifproductand(product.product_tmpl_id.has_dynamic_attributes()orproduct.product_tmpl_id._has_no_variant_attributes())andnotline_idandnotkwargs.get('force_search',False):
            returnself.env['sale.order.line']

        domain=[('order_id','=',self.id),('product_id','=',product_id)]
        ifline_id:
            domain+=[('id','=',line_id)]
        else:
            domain+=[('product_custom_attribute_value_ids','=',False)]

        returnself.env['sale.order.line'].sudo().search(domain)

    def_website_product_id_change(self,order_id,product_id,qty=0):
        order=self.sudo().browse(order_id)
        product_context=dict(self.env.context)
        product_context.setdefault('lang',order.partner_id.lang)
        product_context.update({
            'partner':order.partner_id,
            'quantity':qty,
            'date':order.date_order,
            'pricelist':order.pricelist_id.id,
        })
        product=self.env['product.product'].with_context(product_context).with_company(order.company_id.id).browse(product_id)
        discount=0

        iforder.pricelist_id.discount_policy=='without_discount':
            #Thispartisprettymuchacopy-pasteofthemethod'_onchange_discount'of
            #'sale.order.line'.
            price,rule_id=order.pricelist_id.with_context(product_context).get_product_price_rule(product,qtyor1.0,order.partner_id)
            pu,currency=request.env['sale.order.line'].with_context(product_context)._get_real_price_currency(product,rule_id,qty,product.uom_id,order.pricelist_id.id)
            iforder.pricelist_idandorder.partner_id:
                order_line=order._cart_find_product_line(product.id)
                iforder_line:
                    price=product._get_tax_included_unit_price(
                        self.company_id,
                        order.currency_id,
                        order.date_order,
                        'sale',
                        fiscal_position=order.fiscal_position_id,
                        product_price_unit=price,
                        product_currency=order.currency_id
                    )
                    pu=product._get_tax_included_unit_price(
                        self.company_id,
                        order.currency_id,
                        order.date_order,
                        'sale',
                        fiscal_position=order.fiscal_position_id,
                        product_price_unit=pu,
                        product_currency=order.currency_id
                    )
            ifpu!=0:
                iforder.pricelist_id.currency_id!=currency:
                    #weneednew_list_priceinthesamecurrencyasprice,whichisintheSO'spricelist'scurrency
                    date=order.date_orderorfields.Date.today()
                    pu=currency._convert(pu,order.pricelist_id.currency_id,order.company_id,date)
                discount=(pu-price)/pu*100
                ifdiscount<0:
                    #Incasethediscountisnegative,wedon'twanttoshowittothecustomer,
                    #butwestillwanttousethepricedefinedonthepricelist
                    discount=0
                    pu=price
            else:
                #Incasetheprice_unitequal0andthereforenotabletocalculatethediscount,
                #wefallbackonthepricedefinedonthepricelist.
                pu=price
        else:
            pu=product.price
            iforder.pricelist_idandorder.partner_id:
                order_line=order._cart_find_product_line(product.id,force_search=True)
                iforder_line:
                    pu=product._get_tax_included_unit_price(
                        self.company_id,
                        order.currency_id,
                        order.date_order,
                        'sale',
                        fiscal_position=order.fiscal_position_id,
                        product_price_unit=product.price,
                        product_currency=order.currency_id
                    )

        return{
            'product_id':product_id,
            'product_uom_qty':qty,
            'order_id':order_id,
            'product_uom':product.uom_id.id,
            'price_unit':pu,
            'discount':discount,
        }

    def_cart_update(self,product_id=None,line_id=None,add_qty=0,set_qty=0,**kwargs):
        """Addorsetproductquantity,add_qtycanbenegative"""
        self.ensure_one()
        product_context=dict(self.env.context)
        product_context.setdefault('lang',self.sudo().partner_id.lang)
        SaleOrderLineSudo=self.env['sale.order.line'].sudo().with_context(product_context)
        #changelangtogetcorrectnameofattributes/values
        product_with_context=self.env['product.product'].with_context(product_context)
        product=product_with_context.browse(int(product_id)).exists()

        ifnotproductor(notline_idandnotproduct._is_add_to_cart_allowed()):
            raiseUserError(_("Thegivenproductdoesnotexistthereforeitcannotbeaddedtocart."))

        try:
            ifadd_qty:
                add_qty=int(add_qty)
        exceptValueError:
            add_qty=1
        try:
            ifset_qty:
                set_qty=int(set_qty)
        exceptValueError:
            set_qty=0
        quantity=0
        order_line=False
        ifself.state!='draft':
            request.session['sale_order_id']=None
            raiseUserError(_('Itisforbiddentomodifyasalesorderwhichisnotindraftstatus.'))
        ifline_idisnotFalse:
            order_line=self._cart_find_product_line(product_id,line_id,**kwargs)[:1]

        #Createlineifnolinewithproduct_idcanbelocated
        ifnotorder_line:
            no_variant_attribute_values=kwargs.get('no_variant_attribute_values')or[]
            received_no_variant_values=product.env['product.template.attribute.value'].browse([int(ptav['value'])forptavinno_variant_attribute_values])
            received_combination=product.product_template_attribute_value_ids|received_no_variant_values
            product_template=product.product_tmpl_id

            #handleallcaseswhereincorrectorincompletedataarereceived
            combination=product_template._get_closest_possible_combination(received_combination)

            #getorcreate(ifdynamic)thecorrectvariant
            product=product_template._create_product_variant(combination)

            ifnotproduct:
                raiseUserError(_("Thegivencombinationdoesnotexistthereforeitcannotbeaddedtocart."))

            product_id=product.id

            values=self._website_product_id_change(self.id,product_id,qty=1)

            #addno_variantattributesthatwerenotreceived
            forptavincombination.filtered(lambdaptav:ptav.attribute_id.create_variant=='no_variant'andptavnotinreceived_no_variant_values):
                no_variant_attribute_values.append({
                    'value':ptav.id,
                })

            #saveno_variantattributesvalues
            ifno_variant_attribute_values:
                values['product_no_variant_attribute_value_ids']=[
                    (6,0,[int(attribute['value'])forattributeinno_variant_attribute_values])
                ]

            #addis_customattributevaluesthatwerenotreceived
            custom_values=kwargs.get('product_custom_attribute_values')or[]
            received_custom_values=product.env['product.template.attribute.value'].browse([int(ptav['custom_product_template_attribute_value_id'])forptavincustom_values])

            forptavincombination.filtered(lambdaptav:ptav.is_customandptavnotinreceived_custom_values):
                custom_values.append({
                    'custom_product_template_attribute_value_id':ptav.id,
                    'custom_value':'',
                })

            #saveis_customattributesvalues
            ifcustom_values:
                values['product_custom_attribute_value_ids']=[(0,0,{
                    'custom_product_template_attribute_value_id':custom_value['custom_product_template_attribute_value_id'],
                    'custom_value':custom_value['custom_value']
                })forcustom_valueincustom_values]

            #createtheline
            order_line=SaleOrderLineSudo.create(values)

            try:
                order_line._compute_tax_id()
            exceptValidationErrorase:
                #Thevalidationmayoccurinbackend(eg:taxcloud)butshouldfailsilentlyinfrontend
                _logger.debug("ValidationErroroccursduringtaxcompute.%s"%(e))
            ifadd_qty:
                add_qty-=1

        #computenewquantity
        ifset_qty:
            quantity=set_qty
        elifadd_qtyisnotNone:
            quantity=order_line.product_uom_qty+(add_qtyor0)

        #Removezeroofnegativelines
        ifquantity<=0:
            linked_line=order_line.linked_line_id
            order_line.unlink()
            iflinked_line:
                #updatedescriptionoftheparent
                linked_product=product_with_context.browse(linked_line.product_id.id)
                linked_line.name=linked_line.get_sale_order_line_multiline_description_sale(linked_product)
        else:
            #updateline
            no_variant_attributes_price_extra=[ptav.price_extraforptavinorder_line.product_no_variant_attribute_value_ids]
            values=self.with_context(no_variant_attributes_price_extra=tuple(no_variant_attributes_price_extra))._website_product_id_change(self.id,product_id,qty=quantity)
            order=self.sudo().browse(self.id)
            ifself.pricelist_id.discount_policy=='with_discount'andnotself.env.context.get('fixed_price'):
                product_context.update({
                    'partner':order.partner_id,
                    'quantity':quantity,
                    'date':order.date_order,
                    'pricelist':order.pricelist_id.id,
                })
            product_with_context=self.env['product.product'].with_context(product_context).with_company(order.company_id.id)
            product=product_with_context.browse(product_id)

            order_line.write(values)

            #linkaproducttothesalesorder
            ifkwargs.get('linked_line_id'):
                linked_line=SaleOrderLineSudo.browse(kwargs['linked_line_id'])
                order_line.write({
                    'linked_line_id':linked_line.id,
                })
                linked_product=product_with_context.browse(linked_line.product_id.id)
                linked_line.name=linked_line.get_sale_order_line_multiline_description_sale(linked_product)
            #Generatethedescriptionwitheverything.Thisisdoneafter
            #creatingbecausethefollowingrelatedfieldshavetobeset:
            #-product_no_variant_attribute_value_ids
            #-product_custom_attribute_value_ids
            #-linked_line_id
            order_line.name=order_line.get_sale_order_line_multiline_description_sale(product)

        option_lines=self.order_line.filtered(lambdal:l.linked_line_id.id==order_line.id)

        return{'line_id':order_line.id,'quantity':quantity,'option_ids':list(set(option_lines.ids))}

    def_cart_accessories(self):
        """Suggestaccessoriesbasedon'AccessoryProducts'ofproductsincart"""
        fororderinself:
            products=order.website_order_line.mapped('product_id')
            accessory_products=self.env['product.product']
            forlineinorder.website_order_line.filtered(lambdal:l.product_id):
                combination=line.product_id.product_template_attribute_value_ids+line.product_no_variant_attribute_value_ids
                accessory_products|=line.product_id.accessory_product_ids.filtered(lambdaproduct:
                    product.website_publishedand
                    productnotinproductsand
                    product._is_variant_possible(parent_combination=combination)and
                    (product.company_id==line.company_idornotproduct.company_id)
                )

            returnrandom.sample(accessory_products,len(accessory_products))

    defaction_recovery_email_send(self):
        fororderinself:
            order._portal_ensure_token()
        composer_form_view_id=self.env.ref('mail.email_compose_message_wizard_form').id

        template_id=self._get_cart_recovery_template().id

        return{
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':'mail.compose.message',
            'view_id':composer_form_view_id,
            'target':'new',
            'context':{
                'default_composition_mode':'mass_mail'iflen(self.ids)>1else'comment',
                'default_res_id':self.ids[0],
                'default_model':'sale.order',
                'default_use_template':bool(template_id),
                'default_template_id':template_id,
                'website_sale_send_recovery_email':True,
                'active_ids':self.ids,
            },
        }

    def_get_cart_recovery_template(self):
        """
        Returnthecartrecoverytemplaterecordforasetoforders.
        Iftheyallbelongtothesamewebsite,wereturnthewebsite-specifictemplate;
        otherwisewereturnthedefaulttemplate.
        Ifthedefaultisnotfound,theempty['mail.template']isreturned.
        """
        websites=self.mapped('website_id')
        template=websites.cart_recovery_mail_template_idiflen(websites)==1elseFalse
        template=templateorself.env.ref('website_sale.mail_template_sale_cart_recovery',raise_if_not_found=False)
        returntemplateorself.env['mail.template']

    def_cart_recovery_email_send(self):
        """Sendthecartrecoveryemailonthecurrentrecordset,
        makingsurethattheportaltokenexiststoavoidbrokenlinks,andmarkingtheemailassent.
        Similarmethodtoaction_recovery_email_send,madetobecalledinautomatedactions.
        Contrarytotheformer,itwillusethewebsite-specifictemplateforeachorder."""
        sent_orders=self.env['sale.order']
        fororderinself:
            template=order._get_cart_recovery_template()
            iftemplate:
                order._portal_ensure_token()
                template.send_mail(order.id)
                sent_orders|=order
        sent_orders.write({'cart_recovery_email_sent':True})

    defaction_confirm(self):
        res=super(SaleOrder,self).action_confirm()
        fororderinself:
            ifnotorder.transaction_idsandnotorder.amount_totalandself._context.get('send_email'):
                order._send_order_confirmation_mail()
        returnres


classSaleOrderLine(models.Model):
    _inherit="sale.order.line"

    name_short=fields.Char(compute="_compute_name_short")

    linked_line_id=fields.Many2one('sale.order.line',string='LinkedOrderLine',domain="[('order_id','=',order_id)]",ondelete='cascade',copy=False,index=True)
    option_line_ids=fields.One2many('sale.order.line','linked_line_id',string='OptionsLinked')

    defget_sale_order_line_multiline_description_sale(self,product):
        description=super(SaleOrderLine,self).get_sale_order_line_multiline_description_sale(product)
        ifself.linked_line_id:
            description+="\n"+_("Optionfor:%s",self.linked_line_id.product_id.display_name)
        ifself.option_line_ids:
            description+="\n"+'\n'.join([_("Option:%s",option_line.product_id.display_name)foroption_lineinself.option_line_ids])
        returndescription

    @api.depends('product_id.display_name')
    def_compute_name_short(self):
        """Computeashortnameforthissaleorderline,tobeusedonthewebsitewherewedon'thavemuchspace.
            Tokeepitshort,insteadofusingthefirstlineofthedescription,wetaketheproductnamewithouttheinternalreference.
        """
        forrecordinself:
            record.name_short=record.product_id.with_context(display_default_code=False).display_name

    defget_description_following_lines(self):
        returnself.name.splitlines()[1:]
