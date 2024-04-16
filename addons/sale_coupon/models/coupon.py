#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_


classCoupon(models.Model):
    _inherit='coupon.coupon'

    order_id=fields.Many2one('sale.order','OrderReference',readonly=True,
        help="Thesalesorderfromwhichcouponisgenerated")
    sales_order_id=fields.Many2one('sale.order','Usedin',readonly=True,
        help="Thesalesorderonwhichthecouponisapplied")

    def_check_coupon_code(self,order):
        message={}
        applicable_programs=order._get_applicable_programs()
        ifself.state=='used':
            message={'error':_('Thiscouponhasalreadybeenused(%s).')%(self.code)}
        elifself.state=='reserved':
            message={'error':_('Thiscoupon%sexistsbuttheoriginsalesorderisnotvalidatedyet.')%(self.code)}
        elifself.state=='cancel':
            message={'error':_('Thiscouponhasbeencancelled(%s).')%(self.code)}
        elifself.state=='expired'or(self.expiration_dateandself.expiration_date<fields.Datetime.now().date()):
            message={'error':_('Thiscouponisexpired(%s).')%(self.code)}
        #Minimumrequirementshouldnotbecheckedifthecoupongotgeneratedbyapromotionprogram(therequirementshouldhaveonlybecheckedtogeneratethecoupon)
        elifself.program_id.program_type=='coupon_program'andnotself.program_id._filter_on_mimimum_amount(order):
            message={'error':_(
                'Aminimumof%(amount)s%(currency)sshouldbepurchasedtogetthereward',
                amount=self.program_id.rule_minimum_amount,
                currency=self.program_id.currency_id.name
            )}
        elifnotself.program_id.active:
            message={'error':_('Thecouponprogramfor%sisindraftorclosedstate')%(self.code)}
        elifself.partner_idandself.partner_id!=order.partner_id:
            message={'error':_('Invalidpartner.')}
        elifself.program_idinorder.applied_coupon_ids.mapped('program_id'):
            message={'error':_('ACouponisalreadyappliedforthesamereward')}
        elifself.program_id._is_global_discount_program()andorder._is_global_discount_already_applied():
            message={'error':_('Globaldiscountsarenotcumulable.')}
        elifself.program_id.reward_type=='product'andnotorder._is_reward_in_order_lines(self.program_id):
            message={'error':_('Therewardproductsshouldbeinthesalesorderlinestoapplythediscount.')}
        elifnotself.program_id._is_valid_partner(order.partner_id):
            message={'error':_("Thecustomerdoesn'thaveaccesstothisreward.")}
        #Productrequirementshouldnotbecheckedifthecoupongotgeneratedbyapromotionprogram(therequirementshouldhaveonlybecheckedtogeneratethecoupon)
        elifself.program_id.program_type=='coupon_program'andnotself.program_id._filter_programs_on_products(order):
            message={'error':_("Youdon'thavetherequiredproductquantitiesonyoursalesorder.Alltheproductsshouldberecordedonthesalesorder.(Example:Youneedtohave3T-shirtsonyoursalesorderifthepromotionis'Buy2,Get1Free').")}
        else:
            ifself.program_idnotinapplicable_programsandself.program_id.promo_applicability=='on_current_order':
                message={'error':_('Atleastoneoftherequiredconditionsisnotmettogetthereward!')}
        returnmessage
