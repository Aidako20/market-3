#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError,ValidationError

importast


classCouponProgram(models.Model):
    _name='coupon.program'
    _description="CouponProgram"
    _inherits={'coupon.rule':'rule_id','coupon.reward':'reward_id'}
    #Weshouldapply'discount'promotionfirsttoavoidofferingfreeproductwhenweshouldnot.
    #Eg:IfthediscountlowertheSOtotalbelowtherequiredthreshold
    #Note:Thisisonlyrevelantwhenprogramshavethesamesequence(whichtheyhavebydefault)
    _order="sequence,reward_type"

    name=fields.Char(required=True,translate=True)
    active=fields.Boolean('Active',default=True,help="Aprogramisavailableforthecustomerswhenactive")
    rule_id=fields.Many2one('coupon.rule',string="CouponRule",ondelete='restrict',required=True)
    reward_id=fields.Many2one('coupon.reward',string="Reward",ondelete='restrict',required=True,copy=False)
    sequence=fields.Integer(copy=False,
        help="Couponprogramwillbeappliedbasedongivensequenceifmultipleprogramsare"+
        "definedonsamecondition(Forminimumamount)")
    maximum_use_number=fields.Integer(help="Maximumnumberofsalesordersinwhichrewardcanbeprovided")
    program_type=fields.Selection([
        ('promotion_program','PromotionalProgram'),
        ('coupon_program','CouponProgram'),
        ],
        help="""Apromotionalprogramcanbeeitheralimitedpromotionalofferwithoutcode(appliedautomatically)
                orwithacode(displayedonamagazineforexample)thatmaygenerateadiscountonthecurrent
                orderorcreateacouponforanextorder.

                Acouponprogramgeneratescouponswithacodethatcanbeusedtogenerateadiscountonthecurrent
                orderorcreateacouponforanextorder.""")
    promo_code_usage=fields.Selection([
        ('no_code_needed','AutomaticallyApplied'),
        ('code_needed','Useacode')],
        help="AutomaticallyApplied-Nocodeisrequired,iftheprogramrulesaremet,therewardisapplied(Excepttheglobaldiscountorthefreeshippingrewardswhicharenotcumulative)\n"+
             "Useacode-Iftheprogramrulesaremet,avalidcodeismandatoryfortherewardtobeapplied\n")
    promo_code=fields.Char('PromotionCode',copy=False,
        help="Apromotioncodeisacodethatisassociatedwithamarketingdiscount.Forexample,aretailermighttellfrequentcustomerstoenterthepromotioncode'THX001'toreceivea10%%discountontheirwholeorder.")
    promo_applicability=fields.Selection([
        ('on_current_order','ApplyOnCurrentOrder'),
        ('on_next_order','SendaCoupon')],
        default='on_current_order',string="Applicability")
    coupon_ids=fields.One2many('coupon.coupon','program_id',string="GeneratedCoupons",copy=False)
    coupon_count=fields.Integer(compute='_compute_coupon_count')
    company_id=fields.Many2one('res.company',string="Company",default=lambdaself:self.env.company)
    currency_id=fields.Many2one(string="Currency",related='company_id.currency_id',readonly=True)
    validity_duration=fields.Integer(default=30,
        help="Validitydurationforacouponafteritsgeneration")

    @api.constrains('promo_code')
    def_check_promo_code_constraint(self):
        """Programcodemustbeunique"""
        forprograminself.filtered(lambdap:p.promo_code):
            domain=[('id','!=',program.id),('promo_code','=',program.promo_code)]
            ifself.search(domain):
                raiseValidationError(_('Theprogramcodemustbeunique!'))

    @api.depends('coupon_ids')
    def_compute_coupon_count(self):
        coupon_data=self.env['coupon.coupon'].read_group([('program_id','in',self.ids)],['program_id'],['program_id'])
        mapped_data=dict([(m['program_id'][0],m['program_id_count'])formincoupon_data])
        forprograminself:
            program.coupon_count=mapped_data.get(program.id,0)

    @api.onchange('promo_code_usage')
    def_onchange_promo_code_usage(self):
        ifself.promo_code_usage=='no_code_needed':
            self.promo_code=False

    @api.onchange('reward_product_id')
    def_onchange_reward_product_id(self):
        ifself.reward_product_id:
            self.reward_product_uom_id=self.reward_product_id.uom_id

    @api.onchange('discount_type')
    def_onchange_discount_type(self):
        ifself.discount_type=='fixed_amount':
            self.discount_apply_on='on_order'

    @api.model
    defcreate(self,vals):
        program=super(CouponProgram,self).create(vals)
        ifnotvals.get('discount_line_product_id',False):
            values=program._get_discount_product_values()
            discount_line_product_id=self.env['product.product'].create(values)
            program.write({'discount_line_product_id':discount_line_product_id.id})
        returnprogram

    defwrite(self,vals):
        res=super(CouponProgram,self).write(vals)
        ifnotself:
            returnres
        reward_fields=[
            'reward_type','reward_product_id','discount_type','discount_percentage',
            'discount_apply_on','discount_specific_product_ids','discount_fixed_amount'
        ]
        ifany(fieldinreward_fieldsforfieldinvals):
            forprograminself:
                program.discount_line_product_id.write({'name':program.reward_id.display_name})
        returnres

    defunlink(self):
        ifself.filtered('active'):
            raiseUserError(_('Youcannotdeleteaprograminactivestate'))
        #getreferencetoruleandreward
        rule=self.rule_id
        reward=self.reward_id
        #unlinktheprogram
        super(CouponProgram,self).unlink()
        #thenunlinktheruleandreward
        rule.unlink()
        reward.unlink()
        returnTrue

    deftoggle_active(self):
        super(CouponProgram,self).toggle_active()
        forprograminself:
            program.discount_line_product_id.active=program.active
        coupons=self.filtered(lambdap:notp.activeandp.promo_code_usage=='code_needed').mapped('coupon_ids')
        coupons.filtered(lambdax:x.state!='used').write({'state':'expired'})

    def_compute_program_amount(self,field,currency_to):
        self.ensure_one()
        returnself.currency_id._convert(self[field],currency_to,self.company_id,fields.Date.today())

    def_is_valid_partner(self,partner):
        ifself.rule_partners_domainandself.rule_partners_domain!='[]':
            domain=ast.literal_eval(self.rule_partners_domain)+[('id','=',partner.id)]
            returnbool(self.env['res.partner'].search_count(domain))
        else:
            returnTrue

    def_is_valid_product(self,product):
        """Checkifthegivenproductisvalidfortheprogram.

        :paramproduct:recordofproduct.product
        :rtype:bool
        """
        returnbool(self._get_valid_products(product))

    def_get_valid_products(self,products):
        """Getvalidproductsfortheprogram.

        :paramproducts:recordsofproduct.product
        :return:validproductsrecordset
        """
        ifself.rule_products_domainandself.rule_products_domain!="[]":
            domain=ast.literal_eval(self.rule_products_domain)
            returnproducts.filtered_domain(domain)
        returnproducts

    def_get_discount_product_values(self):
        return{
            'name':self.reward_id.display_name,
            'type':'service',
            'taxes_id':False,
            'supplier_taxes_id':False,
            'sale_ok':False,
            'purchase_ok':False,
            'lst_price':0,#Donotsetahighvaluetoavoidissuewithcouponcode
        }
