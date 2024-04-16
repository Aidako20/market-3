#-*-coding:utf-8-*-

fromflectraimport_,api,fields,models

importast
fromflectra.osvimportexpression


classCouponGenerate(models.TransientModel):
    _name='coupon.generate.wizard'
    _description='GenerateCoupon'

    nbr_coupons=fields.Integer(string="NumberofCoupons",help="Numberofcoupons",default=1)
    generation_type=fields.Selection([
        ('nbr_coupon','NumberofCoupons'),
        ('nbr_customer','NumberofSelectedCustomers')
        ],default='nbr_coupon')
    partners_domain=fields.Char(string="Customer",default='[]')
    has_partner_email=fields.Boolean(compute='_compute_has_partner_email')

    defgenerate_coupon(self):
        """Generatesthenumberofcouponsenteredinwizardfieldnbr_coupons
        """
        program=self.env['coupon.program'].browse(self.env.context.get('active_id'))

        vals={'program_id':program.id}

        ifself.generation_type=='nbr_coupon'andself.nbr_coupons>0:
            forcountinrange(0,self.nbr_coupons):
                self.env['coupon.coupon'].create(vals)

        ifself.generation_type=='nbr_customer'andself.partners_domain:
            forpartnerinself.env['res.partner'].search(ast.literal_eval(self.partners_domain)):
                vals.update({'partner_id':partner.id,'state':'sent'ifpartner.emailelse'new'})
                coupon=self.env['coupon.coupon'].create(vals)
                context=dict(lang=partner.lang)
                subject=_('%s,acouponhasbeengeneratedforyou')%(partner.name)
                delcontext
                template=self.env.ref('coupon.mail_template_sale_coupon',raise_if_not_found=False)
                iftemplate:
                    email_values={'email_from':self.env.user.emailor'','subject':subject}
                    template.send_mail(coupon.id,email_values=email_values,notif_layout='mail.mail_notification_light')

    @api.depends('partners_domain')
    def_compute_has_partner_email(self):
        forrecordinself:
            partners_domain=ast.literal_eval(record.partners_domain)
            ifpartners_domain==[['','=',1]]:
                #Thefieldnameisnotclear.Itactuallymeans"allpartnershaveemail".
                #Ifdomainisnotset,wedon'twanttoshowthewarning"thereisapartnerwithoutemail".
                #So,weexplicitlysetvaluetoTrue
                record.has_partner_email=True
                continue
            domain=expression.AND([partners_domain,[('email','=',False)]])
            record.has_partner_email=self.env['res.partner'].search_count(domain)==0
