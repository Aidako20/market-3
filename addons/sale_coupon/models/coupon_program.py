#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_


classCouponProgram(models.Model):
    _inherit='coupon.program'

    order_count=fields.Integer(compute='_compute_order_count')

    #Theapi.dependsishandledin`defmodified`of`sale_coupon/models/sale_order.py`
    def_compute_order_count(self):
        product_data=self.env['sale.order.line'].read_group([('product_id','in',self.mapped('discount_line_product_id').ids)],['product_id'],['product_id'])
        mapped_data=dict([(m['product_id'][0],m['product_id_count'])forminproduct_data])
        forprograminself:
            program.order_count=mapped_data.get(program.discount_line_product_id.id,0)

    defaction_view_sales_orders(self):
        self.ensure_one()
        orders=self.env['sale.order.line'].search([('product_id','=',self.discount_line_product_id.id)]).mapped('order_id')
        return{
            'name':_('SalesOrders'),
            'view_mode':'tree,form',
            'res_model':'sale.order',
            'search_view_id':[self.env.ref('sale.sale_order_view_search_inherit_quotation').id],
            'type':'ir.actions.act_window',
            'domain':[('id','in',orders.ids)],
            'context':dict(self._context,create=False),
        }

    def_check_promo_code(self,order,coupon_code):
        message={}
        ifself.maximum_use_number!=0andself.order_count>=self.maximum_use_number:
            message={'error':_('Promocode%shasbeenexpired.')%(coupon_code)}
        elifnotself._filter_on_mimimum_amount(order):
            message={'error':_(
                'Aminimumof%(amount)s%(currency)sshouldbepurchasedtogetthereward',
                amount=self.rule_minimum_amount,
                currency=self.currency_id.name
            )}
        elifself.promo_codeandself.promo_code==order.promo_code:
            message={'error':_('Thepromocodeisalreadyappliedonthisorder')}
        elifselfinorder.no_code_promo_program_ids:
            message={'error':_('Thepromotionalofferisalreadyappliedonthisorder')}
        elifnotself.active:
            message={'error':_('Promocodeisinvalid')}
        elifself.rule_date_fromandself.rule_date_from>fields.Datetime.now()orself.rule_date_toandfields.Datetime.now()>self.rule_date_to:
            message={'error':_('Promocodeisexpired')}
        eliforder.promo_codeandself.promo_code_usage=='code_needed':
            message={'error':_('Promotionalscodesarenotcumulative.')}
        elifself._is_global_discount_program()andorder._is_global_discount_already_applied():
            message={'error':_('Globaldiscountsarenotcumulative.')}
        elifself.promo_applicability=='on_current_order'andself.reward_type=='product'andnotorder._is_reward_in_order_lines(self):
            message={'error':_('Therewardproductsshouldbeinthesalesorderlinestoapplythediscount.')}
        elifnotself._is_valid_partner(order.partner_id):
            message={'error':_("Thecustomerdoesn'thaveaccesstothisreward.")}
        elifnotself._filter_programs_on_products(order):
            message={'error':_("Youdon'thavetherequiredproductquantitiesonyoursalesorder.Iftherewardissameproductquantity,pleasemakesurethatalltheproductsarerecordedonthesalesorder(Example:Youneedtohave3T-shirtsonyoursalesorderifthepromotionis'Buy2,Get1Free'.")}
        elifself.promo_applicability=='on_current_order'andnotself.env.context.get('applicable_coupon'):
            applicable_programs=order._get_applicable_programs()
            ifselfnotinapplicable_programs:
                message={'error':_('Atleastoneoftherequiredconditionsisnotmettogetthereward!')}
        returnmessage

    @api.model
    def_filter_on_mimimum_amount(self,order):
        no_effect_lines=order._get_no_effect_on_threshold_lines()
        order_amount={
            'amount_untaxed':order.amount_untaxed-sum(line.price_subtotalforlineinno_effect_lines),
            'amount_tax':order.amount_tax-sum(line.price_taxforlineinno_effect_lines)
        }
        program_ids=list()
        forprograminself:
            ifprogram.reward_type!='discount':
                #avoidthefiltered
                lines=self.env['sale.order.line']
            else:
                lines=order.order_line.filtered(lambdaline:
                    line.product_id==program.discount_line_product_idor
                    line.product_id==program.reward_id.discount_line_product_idor
                    (program.program_type=='promotion_program'andline.is_reward_line)
                )
            untaxed_amount=order_amount['amount_untaxed']-sum(line.price_subtotalforlineinlines)
            tax_amount=order_amount['amount_tax']-sum(line.price_taxforlineinlines)
            program_amount=program._compute_program_amount('rule_minimum_amount',order.currency_id)
            ifprogram.rule_minimum_amount_tax_inclusion=='tax_included'andprogram_amount<=(untaxed_amount+tax_amount)orprogram_amount<=untaxed_amount:
                program_ids.append(program.id)

        returnself.browse(program_ids)

    @api.model
    def_filter_on_validity_dates(self,order):
        returnself.filtered(lambdaprogram:
            (notprogram.rule_date_fromorprogram.rule_date_from<=fields.Datetime.now())
            and
            (notprogram.rule_date_toorprogram.rule_date_to>=fields.Datetime.now())
        )

    @api.model
    def_filter_promo_programs_with_code(self,order):
        '''FilterPromoprogramwithcodewithadifferentpromo_codeifapromo_codeisalreadyordered'''
        returnself.filtered(lambdaprogram:program.promo_code_usage=='code_needed'andprogram.promo_code!=order.promo_code)

    def_filter_unexpired_programs(self,order):
        returnself.filtered(
            lambdaprogram:program.maximum_use_number==0
            orprogram.order_count<program.maximum_use_number
            orprogram
            in(order.code_promo_program_id+order.no_code_promo_program_ids)
        )

    def_filter_programs_on_partners(self,order):
        returnself.filtered(lambdaprogram:program._is_valid_partner(order.partner_id))

    def_filter_programs_on_products(self,order):
        """
        Togetvalidprogramsaccordingtoproductlist.
        i.eBuy1imac+get1ipadminifreethencheck1imacisoncartornot
        or Buy1coke+get1cokefreethencheck2cokesareoncartornot
        """
        order_lines=order.order_line.filtered(lambdaline:line.product_id)-order._get_reward_lines()
        products=order_lines.mapped('product_id')
        products_qties=dict.fromkeys(products,0)
        forlineinorder_lines:
            products_qties[line.product_id]+=line.product_uom_qty
        valid_program_ids=list()
        forprograminself:
            ifnotprogram.rule_products_domainorprogram.rule_products_domain=="[]":
                valid_program_ids.append(program.id)
                continue
            valid_products=program._get_valid_products(products)
            ifnotvalid_products:
                #Theprogramcanbedirectlydiscarded
                continue
            ordered_rule_products_qty=sum(products_qties[product]forproductinvalid_products)
            #Avoidprogramif1orderedfooonaprogram'1foo,1freefoo'
            ifprogram.promo_applicability=='on_current_order'and\
               program.reward_type=='product'andprogram._get_valid_products(program.reward_product_id):
                ordered_rule_products_qty-=program.reward_product_quantity
            ifordered_rule_products_qty>=program.rule_min_quantity:
                valid_program_ids.append(program.id)
        returnself.browse(valid_program_ids)

    def_filter_not_ordered_reward_programs(self,order):
        """
        Returnstheprogramswhentherewardisactuallyintheorderlines
        """
        programs=self.env['coupon.program']
        order_products=order.order_line.product_id
        forprograminself:
            ifprogram.reward_type=='product'andprogram.reward_product_idnotinorder_products:
                continue
            elif(
                program.reward_type=='discount'
                andprogram.discount_apply_on=='specific_products'
                andnotany(discount_productinorder_productsfordiscount_productinprogram.discount_specific_product_ids)
            ):
                continue
            programs+=program
        returnprograms

    @api.model
    def_filter_programs_from_common_rules(self,order,next_order=False):
        """Returntheprogramsifeveryconditionsismet
            :paramboolnext_order:istherewardgivenfromapreviousorder
        """
        programs=self
        #Minimumrequirementshouldnotbecheckedifthecoupongotgeneratedbyapromotionprogram(therequirementshouldhaveonlybecheckedtogeneratethecoupon)
        ifnotnext_order:
            programs=programsandprograms._filter_on_mimimum_amount(order)
        ifnotself.env.context.get("no_outdated_coupons"):
            programs=programsandprograms._filter_on_validity_dates(order)
        programs=programsandprograms._filter_unexpired_programs(order)
        programs=programsandprograms._filter_programs_on_partners(order)
        #Productrequirementshouldnotbecheckedifthecoupongotgeneratedbyapromotionprogram(therequirementshouldhaveonlybecheckedtogeneratethecoupon)
        ifnotnext_order:
            programs=programsandprograms._filter_programs_on_products(order)

        programs_curr_order=programs.filtered(lambdap:p.promo_applicability=='on_current_order')
        programs=programs.filtered(lambdap:p.promo_applicability=='on_next_order')
        ifprograms_curr_order:
            #CheckingifrewardsareintheSOshouldnotbeperformedforrewardson_next_order
            programs+=programs_curr_order._filter_not_ordered_reward_programs(order)
        returnprograms

    def_get_discount_product_values(self):
        res=super()._get_discount_product_values()
        res['invoice_policy']='order'
        returnres

    def_is_global_discount_program(self):
        self.ensure_one()
        returnself.promo_applicability=='on_current_order'and\
               self.reward_type=='discount'and\
               self.discount_type=='percentage'and\
               self.discount_apply_on=='on_order'

    def_keep_only_most_interesting_auto_applied_global_discount_program(self):
        '''Givenarecordsetofprograms,removethelessinterestingauto
        appliedglobaldiscounttokeeponlythemostinterestingone.
        Weshouldnottakepromocodeprogramsintoaccountasa10%auto
        appliedisconsideredbetterthana50%promocode,astheusermight
        notknowaboutthepromocode.
        '''
        programs=self.filtered(lambdap:p._is_global_discount_program()andp.promo_code_usage=='no_code_needed')
        ifnotprograms:returnself
        most_interesting_program=max(programs,key=lambdap:p.discount_percentage)
        #removeleastinterestingprograms
        returnself-(programs-most_interesting_program)
