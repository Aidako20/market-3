#-*-coding:utf-8-*-

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError
fromflectra.osvimportexpression


classSaleCouponApplyCode(models.TransientModel):
    _name='sale.coupon.apply.code'
    _rec_name='coupon_code'
    _description='SalesCouponApplyCode'

    coupon_code=fields.Char(string="Code",required=True)

    defprocess_coupon(self):
        """
        Applytheenteredcouponcodeifvalid,raiseanUserErrorotherwise.
        """
        sales_order=self.env['sale.order'].browse(self.env.context.get('active_id'))
        error_status=self.apply_coupon(sales_order,self.coupon_code)
        iferror_status.get('error',False):
            raiseUserError(error_status.get('error',False))
        iferror_status.get('not_found',False):
            raiseUserError(error_status.get('not_found',False))

    defapply_coupon(self,order,coupon_code):
        error_status={}
        program_domain=order._get_coupon_program_domain()
        program_domain=expression.AND([program_domain,[('promo_code','=',coupon_code)]])
        program=self.env['coupon.program'].search(program_domain)
        ifprogram:
            error_status=program._check_promo_code(order,coupon_code)
            ifnoterror_status:
                ifprogram.promo_applicability=='on_next_order':
                    #Avoidcreatingthecouponifitalreadyexist
                    ifprogram.discount_line_product_id.idnotinorder.generated_coupon_ids.filtered(lambdacoupon:coupon.statein['new','reserved']).mapped('discount_line_product_id').ids:
                        coupon=order._create_reward_coupon(program)
                        return{
                            'generated_coupon':{
                                'reward':coupon.program_id.discount_line_product_id.name,
                                'code':coupon.code,
                            }
                        }
                else: #Theprogramisappliedonthisorder
                    #Onlylinkthepromoprogramifrewardlineswerecreated
                    order_line_count=len(order.order_line)
                    order._create_reward_line(program)
                    iforder_line_count<len(order.order_line):
                        order.code_promo_program_id=program
        else:
            coupon=self.env['coupon.coupon'].search([('code','=',coupon_code)],limit=1)
            ifcoupon:
                error_status=coupon._check_coupon_code(order)
                ifnoterror_status:
                    #Consumecoupononlyifrewardlineswerecreated
                    order_line_count=len(order.order_line)
                    order._create_reward_line(coupon.program_id)
                    iforder_line_count<len(order.order_line):
                        order.applied_coupon_ids+=coupon
                        coupon.write({'state':'used'})
            else:
                error_status={'not_found':_('Thiscouponisinvalid(%s).')%(coupon_code)}
        returnerror_status
