#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError


classCouponRule(models.Model):
    _name='coupon.rule'
    _description="CouponRule"

    rule_date_from=fields.Datetime(string="StartDate",help="Couponprogramstartdate")
    rule_date_to=fields.Datetime(string="EndDate",help="Couponprogramenddate")
    rule_partners_domain=fields.Char(string="BasedonCustomers",help="Couponprogramwillworkforselectedcustomersonly")
    rule_products_domain=fields.Char(string="BasedonProducts",default=[['sale_ok','=',True]],help="OnPurchaseofselectedproduct,rewardwillbegiven")
    rule_min_quantity=fields.Integer(string="MinimumQuantity",default=1,
        help="Minimumrequiredproductquantitytogetthereward")
    rule_minimum_amount=fields.Float(default=0.0,help="Minimumrequiredamounttogetthereward")
    rule_minimum_amount_tax_inclusion=fields.Selection([
        ('tax_included','TaxIncluded'),
        ('tax_excluded','TaxExcluded')],default="tax_excluded")

    _sql_constraints=[
        ('check_coupon_rule_dates','check(rule_date_from<rule_date_to)','Thestartdatemustbebeforetheenddate!'),
    ]

    @api.constrains('rule_minimum_amount')
    def_check_rule_minimum_amount(self):
        ifself.filtered(lambdaapplicability:applicability.rule_minimum_amount<0):
            raiseValidationError(_('Minimumpurchasedamountshouldbegreaterthan0'))

    @api.constrains('rule_min_quantity')
    def_check_rule_min_quantity(self):
        ifnotself.rule_min_quantity>0:
            raiseValidationError(_('Minimumquantityshouldbegreaterthan0'))
