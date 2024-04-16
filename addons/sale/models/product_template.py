#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson
importlogging

fromflectraimportapi,fields,models,_
fromflectra.addons.base.models.res_partnerimportWARNING_MESSAGE,WARNING_HELP
fromflectra.exceptionsimportValidationError
fromflectra.tools.float_utilsimportfloat_round

_logger=logging.getLogger(__name__)


classProductTemplate(models.Model):
    _inherit='product.template'

    def_default_visible_expense_policy(self):
        returnself.user_has_groups('analytic.group_analytic_accounting')

    service_type=fields.Selection([('manual','Manuallysetquantitiesonorder')],string='TrackService',
        help="Manuallysetquantitiesonorder:Invoicebasedonthemanuallyenteredquantity,withoutcreatingananalyticaccount.\n"
             "Timesheetsoncontract:Invoicebasedonthetrackedhoursontherelatedtimesheet.\n"
             "Createataskandtrackhours:Createataskonthesalesordervalidationandtracktheworkhours.",
        default='manual')
    sale_line_warn=fields.Selection(WARNING_MESSAGE,'SalesOrderLine',help=WARNING_HELP,required=True,default="no-message")
    sale_line_warn_msg=fields.Text('MessageforSalesOrderLine')
    expense_policy=fields.Selection(
        [('no','No'),('cost','Atcost'),('sales_price','Salesprice')],
        string='Re-InvoiceExpenses',
        default='no',
        help="Expensesandvendorbillscanbere-invoicedtoacustomer."
             "Withthisoption,avalidatedexpensecanbere-invoicetoacustomeratitscostorsalesprice.")
    visible_expense_policy=fields.Boolean("Re-InvoicePolicyvisible",compute='_compute_visible_expense_policy',default=lambdaself:self._default_visible_expense_policy())
    sales_count=fields.Float(compute='_compute_sales_count',string='Sold')
    visible_qty_configurator=fields.Boolean("Quantityvisibleinconfigurator",compute='_compute_visible_qty_configurator')
    invoice_policy=fields.Selection([
        ('order','Orderedquantities'),
        ('delivery','Deliveredquantities')],string='InvoicingPolicy',
        help='OrderedQuantity:Invoicequantitiesorderedbythecustomer.\n'
             'DeliveredQuantity:Invoicequantitiesdeliveredtothecustomer.',
        default='order')

    def_compute_visible_qty_configurator(self):
        forproduct_templateinself:
            product_template.visible_qty_configurator=True

    @api.depends('name')
    def_compute_visible_expense_policy(self):
        visibility=self.user_has_groups('analytic.group_analytic_accounting')
        forproduct_templateinself:
            product_template.visible_expense_policy=visibility


    @api.onchange('sale_ok')
    def_change_sale_ok(self):
        ifnotself.sale_ok:
            self.expense_policy='no'

    @api.depends('product_variant_ids.sales_count')
    def_compute_sales_count(self):
        forproductinself:
            product.sales_count=float_round(sum([p.sales_countforpinproduct.with_context(active_test=False).product_variant_ids]),precision_rounding=product.uom_id.rounding)


    @api.constrains('company_id')
    def_check_sale_product_company(self):
        """Ensuretheproductisnotbeingrestrictedtoasinglecompanywhile
        havingbeensoldinanotheroneinthepast,asthiscouldcauseissues."""
        target_company=self.company_id
        iftarget_company: #don'tpreventwriting`False`,shouldalwayswork
            product_data=self.env['product.product'].sudo().with_context(active_test=False).search_read([('product_tmpl_id','in',self.ids)],fields=['id'])
            product_ids=list(map(lambdap:p['id'],product_data))
            so_lines=self.env['sale.order.line'].sudo().search_read([('product_id','in',product_ids),('company_id','!=',target_company.id)],fields=['id','product_id'])
            used_products=list(map(lambdasol:sol['product_id'][1],so_lines))
            ifso_lines:
                raiseValidationError(_('Thefollowingproductscannotberestrictedtothecompany'
                                        '%sbecausetheyhavealreadybeenusedinquotationsor'
                                        'salesordersinanothercompany:\n%s\n'
                                        'Youcanarchivetheseproductsandrecreatethem'
                                        'withyourcompanyrestrictioninstead,orleavethemas'
                                        'sharedproduct.')%(target_company.name,','.join(used_products)))

    defaction_view_sales(self):
        action=self.env["ir.actions.actions"]._for_xml_id("sale.report_all_channels_sales_action")
        action['domain']=[('product_tmpl_id','in',self.ids)]
        action['context']={
            'pivot_measures':['product_uom_qty'],
            'active_id':self._context.get('active_id'),
            'active_model':'sale.report',
            'search_default_Sales':1,
            'search_default_filter_order_date':1,
        }
        returnaction

    defcreate_product_variant(self,product_template_attribute_value_ids):
        """Createifnecessaryandpossibleandreturntheidoftheproduct
        variantmatchingthegivencombinationforthistemplate.

        NoteAWA:Known"exploit"issueswiththismethod:

        -Thismethodcouldbeusedbyanunauthenticatedusertogeneratea
            lotofuselessvariants.Unfortunately,afterdiscussingthe
            matterwithODO,there'snoeasyanduser-friendlywaytoblock
            thatbehavior.

            Wewouldhavetousecaptcha/serveractionstoclean/...that
            areallnotuser-friendly/overkillmechanisms.

        -Thismethodcouldbeusedtotrytoguesswhatproductvariantids
            arecreatedinthesystemandwhatproducttemplateidsare
            configuredas"dynamic",butthatdoesnotseemlikeabigdeal.

        Theerrormessagesareidenticalonpurposetoavoidgivingtoomuch
        informationtoapotentialattacker:
            -returning0whenfailing
            -returningthevariantidwhetheritalreadyexistedornot

        :paramproduct_template_attribute_value_ids:thecombinationforwhich
            togetorcreatevariant
        :typeproduct_template_attribute_value_ids:jsonencodedlistofid
            of`product.template.attribute.value`

        :return:idoftheproductvariantmatchingthecombinationor0
        :rtype:int
        """
        combination=self.env['product.template.attribute.value']\
            .browse(json.loads(product_template_attribute_value_ids))

        returnself._create_product_variant(combination,log_warning=True).idor0

    @api.onchange('type')
    def_onchange_type(self):
        """Forcevaluestostayconsistentwithintegrityconstraints"""
        res=super(ProductTemplate,self)._onchange_type()
        ifself.type=='consu':
            ifnotself.invoice_policy:
                self.invoice_policy='order'
            self.service_type='manual'
        ifself._originandself.sales_count>0:
            res['warning']={
                'title':_("Warning"),
                'message':_("Youcannotchangetheproduct'stypebecauseitisalreadyusedinsalesorders.")
            }
        returnres

    @api.model
    defget_import_templates(self):
        res=super(ProductTemplate,self).get_import_templates()
        ifself.env.context.get('sale_multi_pricelist_product_template'):
            ifself.user_has_groups('product.group_sale_pricelist'):
                return[{
                    'label':_('ImportTemplateforProducts'),
                    'template':'/product/static/xls/product_template.xls'
                }]
        returnres

    def_get_combination_info(self,combination=False,product_id=False,add_qty=1,pricelist=False,parent_combination=False,only_template=False):
        """Returninfoaboutagivencombination.

        Note:thismethoddoesnottakeintoaccountwhetherthecombinationis
        actuallypossible.

        :paramcombination:recordsetof`product.template.attribute.value`

        :paramproduct_id:idofa`product.product`.Ifno`combination`
            isset,themethodwilltrytoloadthevariant`product_id`if
            itexistsinsteadoffindingavariantbasedonthecombination.

            Ifthereisnocombination,thatmeanswedefinitelywanta
            variantandnotsomethingthatwillhaveno_variantset.

        :paramadd_qty:floatwiththequantityforwhichtogettheinfo,
            indeedsomepricelistrulesmightdependonit.

        :parampricelist:`product.pricelist`thepricelisttouse
            (canbenone,eg.fromSOifnopartnerandnopricelistselected)

        :paramparent_combination:ifnocombinationandnoproduct_idare
            given,itwilltrytofindthefirstpossiblecombination,taking
            intoaccountparent_combination(ifset)fortheexclusionrules.

        :paramonly_template:boolean,ifsettoTrue,gettheinfoforthe
            templateonly:ignorecombinationanddon'ttrytofindvariant

        :return:dictwithproduct/combinationinfo:

            -product_id:thevariantidmatchingthecombination(ifitexists)

            -product_template_id:thecurrenttemplateid

            -display_name:thenameofthecombination

            -price:thecomputedpriceofthecombination,takethecatalog
                priceifnopricelistisgiven

            -list_price:thecatalogpriceofthecombination,butthisis
                notthe"real"list_price,ithasprice_extraincluded(so
                it'sactuallymorecloselyrelatedto`lst_price`),andit
                isconvertedtothepricelistcurrency(ifgiven)

            -has_discounted_price:Trueifthepricelistdiscountpolicysays
                thepricedoesnotincludethediscountandthereisactuallya
                discountapplied(price<list_price),elseFalse
        """
        self.ensure_one()
        #getthenamebeforethechangeofcontexttobenefitfromprefetch
        display_name=self.display_name

        display_image=True
        quantity=self.env.context.get('quantity',add_qty)
        context=dict(self.env.context,quantity=quantity,pricelist=pricelist.idifpricelistelseFalse)
        product_template=self.with_context(context)

        combination=combinationorproduct_template.env['product.template.attribute.value']

        ifnotproduct_idandnotcombinationandnotonly_template:
            combination=product_template._get_first_possible_combination(parent_combination)

        ifonly_template:
            product=product_template.env['product.product']
        elifproduct_idandnotcombination:
            product=product_template.env['product.product'].browse(product_id)
        else:
            product=product_template._get_variant_for_combination(combination)

        ifproduct:
            #Weneedtoaddtheprice_extrafortheattributesthatarenot
            #inthevariant,typicallythoseoftypeno_variant,butitis
            #possiblethatano_variantattributeisstillinavariantif
            #thetypeoftheattributehasbeenchangedaftercreation.
            no_variant_attributes_price_extra=[
                ptav.price_extraforptavincombination.filtered(
                    lambdaptav:
                        ptav.price_extraand
                        ptavnotinproduct.product_template_attribute_value_ids
                )
            ]
            ifno_variant_attributes_price_extra:
                product=product.with_context(
                    no_variant_attributes_price_extra=tuple(no_variant_attributes_price_extra)
                )
            list_price=product.price_compute('list_price')[product.id]
            price=product.priceifpricelistelselist_price
            display_image=bool(product.image_128)
            display_name=product.display_name
            price_extra=(product.price_extraor0.0)+(sum(no_variant_attributes_price_extra)or0.0)
        else:
            current_attributes_price_extra=[v.price_extraor0.0forvincombination]
            product_template=product_template.with_context(current_attributes_price_extra=current_attributes_price_extra)
            price_extra=sum(current_attributes_price_extra)
            list_price=product_template.price_compute('list_price')[product_template.id]
            price=product_template.priceifpricelistelselist_price
            display_image=bool(product_template.image_128)

            combination_name=combination._get_combination_name()
            ifcombination_name:
                display_name="%s(%s)"%(display_name,combination_name)

        ifpricelistandpricelist.currency_id!=product_template.currency_id:
            list_price=product_template.currency_id._convert(
                list_price,pricelist.currency_id,product_template._get_current_company(pricelist=pricelist),
                fields.Date.today()
            )
            price_extra=product_template.currency_id._convert(
                price_extra,pricelist.currency_id,product_template._get_current_company(pricelist=pricelist),
                fields.Date.today()
            )

        price_without_discount=list_priceifpricelistandpricelist.discount_policy=='without_discount'elseprice
        has_discounted_price=(pricelistorproduct_template).currency_id.compare_amounts(price_without_discount,price)==1

        return{
            'product_id':product.id,
            'product_template_id':product_template.id,
            'display_name':display_name,
            'display_image':display_image,
            'price':price,
            'list_price':list_price,
            'price_extra':price_extra,
            'has_discounted_price':has_discounted_price,
        }

    def_can_be_added_to_cart(self):
        """
        Pre-checkto`_is_add_to_cart_possible`toknowifproductcanbesold.
        """
        returnself.sale_ok

    def_is_add_to_cart_possible(self,parent_combination=None):
        """
        It'spossibletoaddtocart(potentiallyafterconfiguration)if
        thereisatleastonepossiblecombination.

        :paramparent_combination:thecombinationfromwhich`self`isan
            optionaloraccessoryproduct.
        :typeparent_combination:recordset`product.template.attribute.value`

        :return:Trueifit'spossibletoaddtocart,elseFalse
        :rtype:bool
        """
        self.ensure_one()
        ifnotself.activeornotself._can_be_added_to_cart():
            #forperformance:avoidcalling`_get_possible_combinations`
            returnFalse
        returnnext(self._get_possible_combinations(parent_combination),False)isnotFalse

    def_get_current_company_fallback(self,**kwargs):
        """Override:ifapricelistisgiven,fallbacktothecompanyofthe
        pricelistifitisset,otherwiseusetheonefromparentmethod."""
        res=super(ProductTemplate,self)._get_current_company_fallback(**kwargs)
        pricelist=kwargs.get('pricelist')
        returnpricelistandpricelist.company_idorres
