#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.tools.miscimportformatLang


classSaleOrder(models.Model):
    _inherit="sale.order"

    applied_coupon_ids=fields.One2many('coupon.coupon','sales_order_id',string="AppliedCoupons",copy=False)
    generated_coupon_ids=fields.One2many('coupon.coupon','order_id',string="OfferedCoupons",copy=False)
    reward_amount=fields.Float(compute='_compute_reward_total')
    no_code_promo_program_ids=fields.Many2many('coupon.program',string="AppliedImmediatePromoPrograms",
        domain="[('promo_code_usage','=','no_code_needed'),'|',('company_id','=',False),('company_id','=',company_id)]",copy=False)
    code_promo_program_id=fields.Many2one('coupon.program',string="AppliedPromoProgram",
        domain="[('promo_code_usage','=','code_needed'),'|',('company_id','=',False),('company_id','=',company_id)]",copy=False)
    promo_code=fields.Char(related='code_promo_program_id.promo_code',help="Appliedprogramcode",readonly=False)

    @api.depends('order_line')
    def_compute_reward_total(self):
        fororderinself:
            order.reward_amount=sum([line.price_subtotalforlineinorder._get_reward_lines()])

    def_get_no_effect_on_threshold_lines(self):
        self.ensure_one()
        lines=self.env['sale.order.line']
        returnlines

    defrecompute_coupon_lines(self):
        fororderinself:
            order._remove_invalid_reward_lines()
            iforder.state!='cancel':
                order._create_new_no_code_promo_reward_lines()
            order._update_existing_reward_lines()

    @api.returns('self',lambdavalue:value.id)
    defcopy(self,default=None):
        order=super(SaleOrder,self).copy(default)
        reward_line=order._get_reward_lines()
        ifreward_line:
            reward_line.unlink()
            order._create_new_no_code_promo_reward_lines()
        returnorder

    defaction_confirm(self):
        res=super().action_confirm()
        valid_coupon_ids=self.generated_coupon_ids.filtered(lambdacoupon:coupon.statenotin['expired','cancel'])
        valid_coupon_ids.write({'state':'new','partner_id':self.partner_id})
        (self.generated_coupon_ids-valid_coupon_ids).write({'state':'cancel','partner_id':self.partner_id})
        self.applied_coupon_ids.write({'state':'used'})
        self._send_reward_coupon_mail()
        returnres

    def_action_cancel(self):
        res=super()._action_cancel()
        self.generated_coupon_ids.write({'state':'expired'})
        self.applied_coupon_ids.write({'state':'new'})
        self.applied_coupon_ids.sales_order_id=False
        self.recompute_coupon_lines()
        returnres

    defaction_draft(self):
        res=super(SaleOrder,self).action_draft()
        self.generated_coupon_ids.write({'state':'reserved'})
        returnres

    def_get_reward_lines(self):
        self.ensure_one()
        returnself.order_line.filtered(lambdaline:line.is_reward_line)

    def_is_reward_in_order_lines(self,program):
        self.ensure_one()
        order_quantity=sum(self.order_line.filtered(lambdaline:
            line.product_id==program.reward_product_id).mapped('product_uom_qty'))
        returnorder_quantity>=program.reward_product_quantity

    def_is_global_discount_already_applied(self):
        applied_programs=self.no_code_promo_program_ids+\
                           self.code_promo_program_id+\
                           self.applied_coupon_ids.mapped('program_id')
        returnapplied_programs.filtered(lambdaprogram:program._is_global_discount_program())

    def_get_reward_values_product(self,program):
        price_unit=self.order_line.filtered(lambdaline:program.reward_product_id==line.product_id)[0].price_reduce

        order_lines=(self.order_line-self._get_reward_lines()).filtered(lambdax:program._get_valid_products(x.product_id))
        max_product_qty=sum(order_lines.mapped('product_uom_qty'))or1
        total_qty=sum(self.order_line.filtered(lambdax:x.product_id==program.reward_product_id).mapped('product_uom_qty'))
        #Removeneededquantityfromrewardquantityifsamerewardandruleproduct
        ifprogram._get_valid_products(program.reward_product_id):
            #numberoftimestheprogramcouldbeappliedbyquantity
            nbr_program_by_qtt=(
                max_product_qty//(program.rule_min_quantity+program.reward_product_quantity)
            )
            #donotgivemorefreerewardthanproducts
            nbr_program_less_than_products=total_qty//program.reward_product_quantity
            program_in_order=min(nbr_program_by_qtt,nbr_program_less_than_products)
            ifprogram.rule_minimum_amount:
                #Ensuretheminimumamountfortherewardismet
                min_amount_with_reward=(
                    program.rule_minimum_amount
                    +program.reward_product_quantity*program.reward_product_id.lst_price
                )
                nbr_program_by_amount=(
                    sum(order_lines.mapped('price_total'))//min_amount_with_reward
                )
                program_in_order=min(program_in_order,nbr_program_by_amount)
            #multipliedbytherewardqty
            reward_product_qty=program_in_order*program.reward_product_quantity
        else:
            program_in_order=max_product_qty//program.rule_min_quantity
            reward_product_qty=min(program.reward_product_quantity*program_in_order,total_qty)

        reward_qty=min(int(int(max_product_qty/program.rule_min_quantity)*program.reward_product_quantity),reward_product_qty)
        #Takethedefaulttaxesontherewardproduct,mappedwiththefiscalposition
        taxes=program.reward_product_id.taxes_id.filtered(lambdat:t.company_id.id==self.company_id.id)
        taxes=self.fiscal_position_id.map_tax(taxes)
        return{
            'product_id':program.discount_line_product_id.id,
            'price_unit':-price_unit,
            'product_uom_qty':reward_qty,
            'is_reward_line':True,
            'name':_("FreeProduct")+"-"+program.reward_product_id.name,
            'product_uom':program.reward_product_id.uom_id.id,
            'tax_id':[(4,tax.id,False)fortaxintaxes],
        }

    def_get_paid_order_lines(self):
        """Returnsthesaleorderlinesthatarenotrewardlines.
            Itwillalsoreturnrewardlinesbeingfreeproductlines."""
        free_reward_product=self.env['coupon.program'].search([('reward_type','=','product')]).mapped('discount_line_product_id')
        returnself.order_line.filtered(lambdax:notx.is_reward_lineorx.product_idinfree_reward_product)

    def_get_base_order_lines(self,program):
        """Returnsthesaleorderlinesnotlinkedtothegivenprogram.
        """
        returnself.order_line.filtered(lambdax:not(x.is_reward_lineandx.product_id==program.discount_line_product_id))

    def_get_reward_values_discount_fixed_amount(self,program):
        total_amount=sum(self._get_base_order_lines(program).mapped('price_total'))
        fixed_amount=program._compute_program_amount('discount_fixed_amount',self.currency_id)
        iftotal_amount<fixed_amount:
            returntotal_amount
        else:
            returnfixed_amount

    def_get_coupon_program_domain(self):
        return[]

    def_get_cheapest_line(self):
        #Unitpricestaxincluded
        returnmin(self.order_line.filtered(lambdax:notx.is_reward_lineandx.price_reduce>0),key=lambdax:x['price_reduce'])

    def_get_reward_values_discount_percentage_per_line(self,program,line):
        discount_amount=line.product_uom_qty*line.price_reduce*(program.discount_percentage/100)
        returndiscount_amount

    def_get_max_reward_values_per_tax(self,program,taxes):
        lines=self.order_line.filtered(lambdal:l.tax_id==taxesandl.product_id!=program.discount_line_product_id)
        returnsum(lines.mapped(lambdal:l.price_reduce*l.product_uom_qty))

    def_get_reward_values_fixed_amount(self,program):
        discount_amount=self._get_reward_values_discount_fixed_amount(program)

        #Incasethereisataxsetonthepromotionproduct,wegiveprioritytoit.
        #Thisallowmanualoverwriteoftaxesforpromotion.
        ifprogram.discount_line_product_id.taxes_id:
            line_taxes=self.fiscal_position_id.map_tax(program.discount_line_product_id.taxes_id)ifself.fiscal_position_idelseprogram.discount_line_product_id.taxes_id
            lines=self._get_base_order_lines(program)
            discount_amount=min(
                sum(lines.mapped(lambdal:l.price_reduce*l.product_uom_qty)),discount_amount
            )
            return[{
                'name':_("Discount:%s",program.name),
                'product_id':program.discount_line_product_id.id,
                'price_unit':-discount_amount,
                'product_uom_qty':1.0,
                'product_uom':program.discount_line_product_id.uom_id.id,
                'is_reward_line':True,
                'tax_id':[(4,tax.id,False)fortaxinline_taxes],
            }]

        lines=self._get_paid_order_lines()
        #RemoveFreeLines
        lines=lines.filtered('price_reduce')
        reward_lines={}

        tax_groups=set([line.tax_idforlineinlines])
        max_discount_per_tax_groups={tax_ids:self._get_max_reward_values_per_tax(program,tax_ids)fortax_idsintax_groups}

        fortax_idsinsorted(tax_groups,key=lambdatax_ids:max_discount_per_tax_groups[tax_ids],reverse=True):

            ifdiscount_amount<=0:
                returnreward_lines.values()

            curr_lines=lines.filtered(lambdal:l.tax_id==tax_ids)
            lines_price=sum(curr_lines.mapped(lambdal:l.price_reduce*l.product_uom_qty))
            lines_total=sum(curr_lines.mapped('price_total'))

            discount_line_amount_price=min(max_discount_per_tax_groups[tax_ids],(discount_amount*lines_price/lines_total))

            ifnotdiscount_line_amount_price:
                continue

            discount_amount-=discount_line_amount_price*lines_total/lines_price

            reward_lines[tax_ids]={
                'name':_(
                    "Discount:%(program)s-Onproductwithfollowingtaxes:%(taxes)s",
                    program=program.name,
                    taxes=",".join(tax_ids.mapped('name')),
                ),
                'product_id':program.discount_line_product_id.id,
                'price_unit':-discount_line_amount_price,
                'product_uom_qty':1.0,
                'product_uom':program.discount_line_product_id.uom_id.id,
                'is_reward_line':True,
                'tax_id':[(4,tax.id,False)fortaxintax_ids],
                }
        returnreward_lines.values()

    def_get_reward_values_discount(self,program):
        ifprogram.discount_type=='fixed_amount':
            returnself._get_reward_values_fixed_amount(program)
        else:
            returnself._get_reward_values_percentage_amount(program)

    def_get_reward_values_percentage_amount(self,program):
        #Invalidatemultilinefixed_pricediscountlineastheyshouldapplyafter%discount
        fixed_price_products=self._get_applied_programs().filtered(
            lambdap:p.discount_type=='fixed_amount'
        ).mapped('discount_line_product_id')
        self.order_line.filtered(lambdal:l.product_idinfixed_price_products).write({'price_unit':0})

        reward_dict={}
        lines=self._get_paid_order_lines()
        amount_total=sum([any(line.tax_id.mapped('price_include'))andline.price_totalorline.price_subtotal
                            forlineinself._get_base_order_lines(program)])
        ifprogram.discount_apply_on=='cheapest_product':
            line=self._get_cheapest_line()
            ifline:
                discount_line_amount=min(line.price_reduce*(program.discount_percentage/100),amount_total)
                ifdiscount_line_amount:
                    taxes=self.fiscal_position_id.map_tax(line.tax_id)

                    reward_dict[line.tax_id]={
                        'name':_("Discount:%s",program.name),
                        'product_id':program.discount_line_product_id.id,
                        'price_unit':-discount_line_amountifdiscount_line_amount>0else0,
                        'product_uom_qty':1.0,
                        'product_uom':program.discount_line_product_id.uom_id.id,
                        'is_reward_line':True,
                        'tax_id':[(4,tax.id,False)fortaxintaxes],
                    }
        elifprogram.discount_apply_onin['specific_products','on_order']:
            ifprogram.discount_apply_on=='specific_products':
                #Weshouldnotexcluderewardlinethatofferthisproductsinceweneedtoofferonlythediscountontherealpaidproduct(regularproduct-freeproduct)
                free_product_lines=self.env['coupon.program'].search([('reward_type','=','product'),('reward_product_id','in',program.discount_specific_product_ids.ids)]).mapped('discount_line_product_id')
                lines=lines.filtered(lambdax:x.product_idin(program.discount_specific_product_ids|free_product_lines))

            #whenprocessinglinesweshouldnotdiscountmorethantheorderremainingtotal
            currently_discounted_amount=0
            forlineinlines:
                discount_line_amount=min(self._get_reward_values_discount_percentage_per_line(program,line),amount_total-currently_discounted_amount)

                ifdiscount_line_amount:

                    ifline.tax_idinreward_dict:
                        reward_dict[line.tax_id]['price_unit']-=discount_line_amount
                    else:
                        taxes=self.fiscal_position_id.map_tax(line.tax_id)

                        reward_dict[line.tax_id]={
                            'name':_(
                                "Discount:%(program)s-Onproductwithfollowingtaxes:%(taxes)s",
                                program=program.name,
                                taxes=",".join(taxes.mapped('name')),
                            ),
                            'product_id':program.discount_line_product_id.id,
                            'price_unit':-discount_line_amountifdiscount_line_amount>0else0,
                            'product_uom_qty':1.0,
                            'product_uom':program.discount_line_product_id.uom_id.id,
                            'is_reward_line':True,
                            'tax_id':[(4,tax.id,False)fortaxintaxes],
                        }
                        currently_discounted_amount+=discount_line_amount

        #Ifthereisamaxamountfordiscount,wemighthavetolimitsomediscountlinesorcompletelyremovesomelines
        max_amount=program._compute_program_amount('discount_max_amount',self.currency_id)
        ifmax_amount>0:
            amount_already_given=0
            forvalinlist(reward_dict):
                amount_to_discount=amount_already_given+reward_dict[val]["price_unit"]
                ifabs(amount_to_discount)>max_amount:
                    reward_dict[val]["price_unit"]=-(max_amount-abs(amount_already_given))
                    add_name=formatLang(self.env,max_amount,currency_obj=self.currency_id)
                    reward_dict[val]["name"]+="("+_("limitedto")+add_name+")"
                amount_already_given+=reward_dict[val]["price_unit"]
                ifreward_dict[val]["price_unit"]==0:
                    delreward_dict[val]
        returnreward_dict.values()

    def_get_reward_line_values(self,program):
        self.ensure_one()
        self=self.with_context(lang=self.partner_id.lang)
        program=program.with_context(lang=self.partner_id.lang)
        values=[]
        ifprogram.reward_type=='discount':
            values=self._get_reward_values_discount(program)
        elifprogram.reward_type=='product':
            values=[self._get_reward_values_product(program)]
        seq=max(self.order_line.mapped('sequence'),default=10)+1
        forvalueinvalues:
            value['sequence']=seq
        returnvalues

    def_create_reward_line(self,program):
        self.write({'order_line':[(0,False,value)forvalueinself._get_reward_line_values(program)]})

    def_create_reward_coupon(self,program):
        #ifthereisalreadyacouponthatwassetasexpired,reactivatethatoneinsteadofcreatinganewone
        coupon=self.env['coupon.coupon'].search([
            ('program_id','=',program.id),
            ('state','=','expired'),
            ('partner_id','=',self.partner_id.id),
            ('order_id','=',self.id),
            ('discount_line_product_id','=',program.discount_line_product_id.id),
        ],limit=1)
        ifcoupon:
            coupon.write({'state':'reserved'})
        else:
            coupon=self.env['coupon.coupon'].sudo().create({
                'program_id':program.id,
                'state':'reserved',
                'partner_id':self.partner_id.id,
                'order_id':self.id,
                'discount_line_product_id':program.discount_line_product_id.id
            })
        self.generated_coupon_ids|=coupon
        returncoupon

    def_send_reward_coupon_mail(self):
        template=self.env.ref('coupon.mail_template_sale_coupon',raise_if_not_found=False)
        iftemplate:
            fororderinself:
                forcouponinorder.generated_coupon_ids.filtered(lambdacoupon:coupon.state=='new'):
                    order.message_post_with_template(
                        template.id,composition_mode='comment',
                        model='coupon.coupon',res_id=coupon.id,
                        email_layout_xmlid='mail.mail_notification_light',
                    )

    def_get_applicable_programs(self):
        """
        Thismethodisusedtoreturnthevalidapplicableprogramsongivenorder.
        """
        self.ensure_one()
        programs=self.env['coupon.program'].with_context(
            no_outdated_coupons=True,
        ).search([
            ('company_id','in',[self.company_id.id,False]),
            '|',('rule_date_from','=',False),('rule_date_from','<=',fields.Datetime.now()),
            '|',('rule_date_to','=',False),('rule_date_to','>=',fields.Datetime.now()),
        ],order="id")._filter_programs_from_common_rules(self)
        #noimpactcode...
        #shouldbeprograms=programs.filteredifwereallywanttofilter...
        #ifself.promo_code:
        #    programs._filter_promo_programs_with_code(self)
        returnprograms

    def_get_applicable_no_code_promo_program(self):
        self.ensure_one()
        programs=self.env['coupon.program'].with_context(
            no_outdated_coupons=True,
            applicable_coupon=True,
        ).search([
            ('promo_code_usage','=','no_code_needed'),
            '|',('rule_date_from','=',False),('rule_date_from','<=',fields.Datetime.now()),
            '|',('rule_date_to','=',False),('rule_date_to','>=',fields.Datetime.now()),
            '|',('company_id','=',self.company_id.id),('company_id','=',False),
        ])._filter_programs_from_common_rules(self)
        returnprograms

    def_get_valid_applied_coupon_program(self):
        self.ensure_one()
        #applied_coupon_ids'scouponsmightbecomingfrom:
        #  *acoupongeneratedfromapreviousorderthatbenefitedfromapromotion_programthatrewardedthenextsaleorder.
        #    Inthatcaserequirementstobenefitfromtheprogram(Quantityandprice)shouldnotbecheckedanymore
        #  *acoupon_program,inthatcasethepromo_applicabilityisalwaysforthecurrentorderandeverythingshouldbechecked(filtered)
        programs=self.applied_coupon_ids.mapped('program_id').filtered(lambdap:p.promo_applicability=='on_next_order')._filter_programs_from_common_rules(self,True)
        programs+=self.applied_coupon_ids.mapped('program_id').filtered(lambdap:p.promo_applicability=='on_current_order')._filter_programs_from_common_rules(self)
        returnprograms

    def_create_new_no_code_promo_reward_lines(self):
        '''Applynewprogramsthatareapplicable'''
        self.ensure_one()
        order=self
        programs=order._get_applicable_no_code_promo_program()
        programs=programs._keep_only_most_interesting_auto_applied_global_discount_program()
        forprograminprograms:
            #VFEREFinmaster_get_applicable_no_code_programsalreadyfiltersprograms
            #whydoweneedtoreapplythisbunchofchecksin_check_promo_code????
            #Weshouldonlyapplyalittlepartofthechecksin_check_promo_code...
            error_status=program._check_promo_code(order,False)
            ifnoterror_status.get('error'):
                ifprogram.promo_applicability=='on_next_order':
                    order.state!='cancel'andorder._create_reward_coupon(program)
                elifprogram.discount_line_product_id.idnotinself.order_line.mapped('product_id').ids:
                    self.write({'order_line':[(0,False,value)forvalueinself._get_reward_line_values(program)]})
                order.no_code_promo_program_ids|=program

    def_update_existing_reward_lines(self):
        '''Updatevaluesforalreadyappliedrewards'''
        defupdate_line(order,lines,values):
            '''Updatethelinesandreturnthemiftheyshouldbedeleted'''
            lines_to_remove=self.env['sale.order.line']
            #movecouponstotheendoftheSO
            values['sequence']=max(order.order_line.mapped('sequence'))+1

            #Checkcommit6bb42904a03fornextif/else
            #Removerewardlineifpriceorqtyequalto0
            ifvalues['product_uom_qty']andvalues['price_unit']:
                lines.write(values)
            else:
                ifprogram.reward_type!='free_shipping':
                    #Can'tremovethelinesdirectlyaswemightbeinarecordsetloop
                    lines_to_remove+=lines
                else:
                    values.update(price_unit=0.0)
                    lines.write(values)
            returnlines_to_remove

        self.ensure_one()
        order=self
        applied_programs=order._get_applied_programs_with_rewards_on_current_order()
        forprograminapplied_programs.sorted(lambdaap:(ap.discount_type=='fixed_amount',ap.discount_apply_on=='on_order')):
            values=order._get_reward_line_values(program)
            lines=order.order_line.filtered(lambdaline:line.product_id==program.discount_line_product_id)
            ifprogram.reward_type=='discount':
                lines_to_remove=lines
                lines_to_add=[]
                lines_to_keep=[]
                #Valuesiswhatdiscountlinesshouldreallybe,linesiswhatwegotintheSOatthemoment
                #1.Ifvalues&linesmatch,weshouldupdatetheline(ordeleteitifnoqtyorprice?)
                #   Asremovingalinesremovealltheotherlineslinkedtothesameprogram,weneedtosavethem
                #   usinglines_to_keep
                #2.Ifthevalueisnotinthelines,weshouldaddit
                #3.ifthelinescontainsataxnotinvalue,weshouldremoveit
                forvalueinvalues:
                    value_found=False
                    forlineinlines:
                        #Case1.
                        ifnotlen(set(line.tax_id.mapped('id')).symmetric_difference(set([v[1]forvinvalue['tax_id']]))):
                            value_found=True
                            #WorkingonCase3.
                            #update_lineupdatethelinetothecorrectvalueandreturnsthemiftheyshouldbeunlinked
                            update_to_remove=update_line(order,line,value)
                            ifnotupdate_to_remove:
                                lines_to_keep+=[(0,False,value)]
                                lines_to_remove-=line
                    #WorkingonCase2.
                    ifnotvalue_found:
                        lines_to_add+=[(0,False,value)]
                #Case3.
                line_update=[]
                iflines_to_remove:
                    line_update+=[(3,line_id,0)forline_idinlines_to_remove.ids]
                    line_update+=lines_to_keep
                line_update+=lines_to_add
                order.write({'order_line':line_update})
            else:
                update_line(order,lines,values[0]).unlink()

    def_remove_invalid_reward_lines(self):
        """Findprograms&couponsthatarenotapplicableanymore.
            Itwillthenunlinktherelatedrewardorderlines.
            Itwillalsounsettheorder'sfieldsthatarestoring
            theappliedcoupons&programs.
            Note:Itwillalsoremovearewardlinecomingfromanarchiveprogram.
        """
        self.ensure_one()
        order=self

        applied_programs=order._get_applied_programs()
        applicable_programs=self.env['coupon.program']
        ifapplied_programs:
            applicable_programs=order._get_applicable_programs()+order._get_valid_applied_coupon_program()
            applicable_programs=applicable_programs._keep_only_most_interesting_auto_applied_global_discount_program()
        programs_to_remove=applied_programs-applicable_programs

        reward_product_ids=applied_programs.discount_line_product_id.ids
        #deleterewardlinecomingfromanarchivedcoupon(itwillneverbeupdated/removedwhenrecomputingtheorder)
        invalid_lines=order.order_line.filtered(lambdaline:line.is_reward_lineandline.product_id.idnotinreward_product_ids)

        ifprograms_to_remove:
            product_ids_to_remove=programs_to_remove.discount_line_product_id.ids

            ifproduct_ids_to_remove:
                #Invalidgeneratedcouponforwhichwearenoteligibleanymore('expired'sinceitisspecifictothisSOandwemayagainmettherequirements)
                self.generated_coupon_ids.filtered(lambdacoupon:coupon.program_id.discount_line_product_id.idinproduct_ids_to_remove).write({'state':'expired'})

            #Resetappliedcouponsforwhichwearenoteligibleanymore('valid'soitcanbeuseonanother)
            coupons_to_remove=order.applied_coupon_ids.filtered(lambdacoupon:coupon.program_idinprograms_to_remove)
            coupons_to_remove.write({'state':'new'})

            #Unbindpromotionandcouponprogramswhichrequirementsarenotmetanymore
            order.no_code_promo_program_ids-=programs_to_remove
            order.code_promo_program_id-=programs_to_remove

            ifcoupons_to_remove:
                order.applied_coupon_ids-=coupons_to_remove

            #Removetheirrewardlines
            ifproduct_ids_to_remove:
                invalid_lines|=order.order_line.filtered(lambdaline:line.product_id.idinproduct_ids_to_remove)

        invalid_lines.unlink()

    def_get_applied_programs_with_rewards_on_current_order(self):
        #Needtoaddfilteroncurrentorder.Indeed,ithasalwaysbeencalculatingrewardlineevenifonnextorder(whichisuselessanddocalculationfornothing)
        #Thisproblemcouldnotbenoticedsinceitwouldonlyupdateordeleteexistinglinesrelatedtothatprogram,itwouldnotfindthelinetoupdatesincenotintheorder
        #Butnowifwedontfindtherewardlineintheorder,weaddit(sincewecannowhavemultiplelineper programincaseofdiscountondifferentvat),thusthebug
        #mentionnedaheadwillbeseennow
        returnself.no_code_promo_program_ids.filtered(lambdap:p.promo_applicability=='on_current_order')+\
               self.applied_coupon_ids.mapped('program_id')+\
               self.code_promo_program_id.filtered(lambdap:p.promo_applicability=='on_current_order')

    def_get_applied_programs_with_rewards_on_next_order(self):
        returnself.no_code_promo_program_ids.filtered(lambdap:p.promo_applicability=='on_next_order')+\
            self.code_promo_program_id.filtered(lambdap:p.promo_applicability=='on_next_order')

    def_get_applied_programs(self):
        """Returnsallappliedprogramsoncurrentorder:

        Expectedtoreturnsameresultthan:

            self._get_applied_programs_with_rewards_on_current_order()
            +
            self._get_applied_programs_with_rewards_on_next_order()
        """
        returnself.code_promo_program_id+self.no_code_promo_program_ids+self.applied_coupon_ids.mapped('program_id')

    def_get_invoice_status(self):
        #Handlingofaspecificsituation:anordercontains
        #aproductinvoicedondeliveryandapromolineinvoiced
        #onorder.Wewouldavoidhavingtheinvoicestatus'to_invoice'
        #ifthecreatedinvoicewillonlycontainthepromotionline
        super()._get_invoice_status()
        fororderinself.filtered(lambdaorder:order.invoice_status=='toinvoice'):
            paid_lines=order._get_paid_order_lines()
            ifnotany(line.invoice_status=='toinvoice'forlineinpaid_lines):
                order.invoice_status='no'

    def_get_invoiceable_lines(self,final=False):
        """Ensureswecannotinvoiceonlyrewardlines.

        Sincepromotionlinesarespecifiedwithserviceproducts,
        thoselinesaredirectlyinvoiceablewhentheorderisconfirmed
        whichcanresultininvoicescontainingonlypromotionlines.

        Toavoidthosecases,weallowtheinvoicingofpromotionlines
        iffatleastanother'basic'linesisalsoinvoiceable.
        """
        invoiceable_lines=super()._get_invoiceable_lines(final)
        reward_lines=self._get_reward_lines()
        ifinvoiceable_lines<=reward_lines:
            returnself.env['sale.order.line'].browse()
        returninvoiceable_lines

    defupdate_prices(self):
        """Recomputecoupons/promotionsafterpricelistpricesreset."""
        super().update_prices()
        ifany(line.is_reward_lineforlineinself.order_line):
            self.recompute_coupon_lines()


classSaleOrderLine(models.Model):
    _inherit="sale.order.line"

    is_reward_line=fields.Boolean('Isaprogramrewardline')

    defunlink(self):
        related_program_lines=self.env['sale.order.line']
        #Reactivatecouponsrelatedtounlinkedrewardline
        forlineinself.filtered(lambdaline:line.is_reward_line):
            coupons_to_reactivate=line.order_id.applied_coupon_ids.filtered(
                lambdacoupon:coupon.program_id.discount_line_product_id==line.product_id
            )
            coupons_to_reactivate.write({'state':'new'})
            line.order_id.applied_coupon_ids-=coupons_to_reactivate
            #Removetheprogramfromtheorderifthedeletedlineistherewardlineoftheprogram
            #Anddeletetheotherlinesfromthisprogram(It'sthecasewhendiscountissplitperdifferenttaxes)
            related_program=self.env['coupon.program'].search([('discount_line_product_id','=',line.product_id.id)])
            ifrelated_program:
                line.order_id.no_code_promo_program_ids-=related_program
                line.order_id.code_promo_program_id-=related_program
                related_program_lines|=line.order_id.order_line.filtered(lambdal:l.product_id.id==related_program.discount_line_product_id.id)-line
        returnsuper(SaleOrderLine,self|related_program_lines).unlink()

    def_compute_tax_id(self):
        reward_lines=self.filtered('is_reward_line')
        super(SaleOrderLine,self-reward_lines)._compute_tax_id()
        #Discountrewardlineissplitpertax,thediscountissetonthelinebutnotontheproduct
        #astheproductisthegenericdiscountline.
        #Incaseofafreeproduct,retrievingthetaxonthelineinsteadoftheproductwon'taffectthebehavior.
        forlineinreward_lines:
            line=line.with_company(line.company_id)
            fpos=line.order_id.fiscal_position_idorline.order_id.fiscal_position_id.get_fiscal_position(line.order_partner_id.id)
            #Ifcompany_idisset,alwaysfiltertaxesbythecompany
            taxes=line.tax_id.filtered(lambdar:notline.company_idorr.company_id==line.company_id)
            line.tax_id=fpos.map_tax(taxes,line.product_id,line.order_id.partner_shipping_id)

    def_get_display_price(self,product):
        #Aproductcreatedfromapromotiondoesnothavealist_price.
        #Theprice_unitofarewardorderlineiscomputedbythepromotion,soitcanbeuseddirectly
        ifself.is_reward_line:
            returnself.price_unit
        returnsuper()._get_display_price(product)

    #Invalidationof`coupon.program.order_count`
    #`test_program_rules_validity_dates_and_uses`,
    #Overridingmodifiedisquitehardcoreasyouneedtoknowhowworksthecacheandtheinvalidationsystem,
    #butatleastthebelowworksandshouldbeefficient.
    #Anotherpossibilityistoaddonproduct.productaone2manytosale.order.line'order_line_ids',
    #andthenaddthedepends@api.depends('discount_line_product_id.order_line_ids'),
    #butIamnotsurethiswillasefficientasthebelow.
    defmodified(self,fnames,*args,**kwargs):
        super(SaleOrderLine,self).modified(fnames,*args,**kwargs)
        if'product_id'infnames:
            Program=self.env['coupon.program'].sudo()
            field_order_count=Program._fields['order_count']
            programs=self.env.cache.get_records(Program,field_order_count)
            ifprograms:
                products=self.filtered('is_reward_line').mapped('product_id')
                forprograminprograms:
                    ifprogram.discount_line_product_idinproducts:
                        self.env.cache.invalidate([(field_order_count,program.ids)])
