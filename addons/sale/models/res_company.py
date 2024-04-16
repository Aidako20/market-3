#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importbase64

fromflectraimportapi,fields,models,_
fromflectra.modules.moduleimportget_module_resource
fromflectra.modules.moduleimportget_resource_path

classResCompany(models.Model):
    _inherit="res.company"

    portal_confirmation_sign=fields.Boolean(string='OnlineSignature',default=True)
    portal_confirmation_pay=fields.Boolean(string='OnlinePayment')
    quotation_validity_days=fields.Integer(default=30,string="DefaultQuotationValidity(Days)")

    #salequotationonboarding
    sale_quotation_onboarding_state=fields.Selection([('not_done',"Notdone"),('just_done',"Justdone"),('done',"Done"),('closed',"Closed")],string="Stateofthesaleonboardingpanel",default='not_done')
    sale_onboarding_order_confirmation_state=fields.Selection([('not_done',"Notdone"),('just_done',"Justdone"),('done',"Done")],string="Stateoftheonboardingconfirmationorderstep",default='not_done')
    sale_onboarding_sample_quotation_state=fields.Selection([('not_done',"Notdone"),('just_done',"Justdone"),('done',"Done")],string="Stateoftheonboardingsamplequotationstep",default='not_done')

    sale_onboarding_payment_method=fields.Selection([
        ('digital_signature','Signonline'),
        ('paypal','PayPal'),
        ('stripe','Stripe'),
        ('other','Paywithanotherpaymentacquirer'),
        ('manual','ManualPayment'),
    ],string="Saleonboardingselectedpaymentmethod")

    @api.model
    defaction_close_sale_quotation_onboarding(self):
        """Marktheonboardingpanelasclosed."""
        self.env.company.sale_quotation_onboarding_state='closed'

    @api.model
    defaction_open_sale_onboarding_payment_acquirer(self):
        """Calledbyonboardingpanelabovethequotationlist."""
        self.env.company.get_chart_of_accounts_or_fail()
        action=self.env["ir.actions.actions"]._for_xml_id("sale.action_open_sale_onboarding_payment_acquirer_wizard")
        returnaction

    def_get_sample_sales_order(self):
        """Getasamplequotationorcreateoneifitdoesnotexist."""
        #usecurrentuseraspartner
        partner=self.env.user.partner_id
        company_id=self.env.company.id
        #istherealreadyone?
        sample_sales_order=self.env['sale.order'].search(
            [('company_id','=',company_id),('partner_id','=',partner.id),
             ('state','=','draft')],limit=1)
        iflen(sample_sales_order)==0:
            sample_sales_order=self.env['sale.order'].create({
                'partner_id':partner.id
            })
            #takeanyexistingproductorcreateone
            product=self.env['product.product'].search([],limit=1)
            iflen(product)==0:
                default_image_path=get_module_resource('product','static/img','product_product_13-image.png')
                product=self.env['product.product'].create({
                    'name':_('SampleProduct'),
                    'active':False,
                    'image_1920':base64.b64encode(open(default_image_path,'rb').read())
                })
                product.product_tmpl_id.write({'active':False})
            self.env['sale.order.line'].create({
                'name':_('SampleOrderLine'),
                'product_id':product.id,
                'product_uom_qty':10,
                'price_unit':123,
                'order_id':sample_sales_order.id,
                'company_id':sample_sales_order.company_id.id,
            })
        returnsample_sales_order

    @api.model
    defaction_open_sale_onboarding_sample_quotation(self):
        """Onboardingstepforsendingasamplequotation.Openawindowtocomposeanemail,
            withtheedi_invoice_templatemessageloadedbydefault."""
        sample_sales_order=self._get_sample_sales_order()
        template=self.env.ref('sale.email_template_edi_sale',False)

        message_composer=self.env['mail.compose.message'].with_context(
            default_use_template=bool(template),
            mark_so_as_sent=True,
            custom_layout='mail.mail_notification_paynow',
            proforma=self.env.context.get('proforma',False),
            force_email=True,mail_notify_author=True
        ).create({
            'res_id':sample_sales_order.id,
            'template_id':templateandtemplate.idorFalse,
            'model':'sale.order',
            'composition_mode':'comment'})

        #Simulatetheonchange(liketriggerinformtheview)
        update_values=message_composer.onchange_template_id(template.id,'comment','sale.order',sample_sales_order.id)['value']
        message_composer.write(update_values)

        message_composer.send_mail()

        self.set_onboarding_step_done('sale_onboarding_sample_quotation_state')

        self.action_close_sale_quotation_onboarding()

        action=self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action.update({
            'views':[[self.env.ref('sale.view_order_form').id,'form']],
            'view_mode':'form',
            'target':'main',
        })
        returnaction

    defget_and_update_sale_quotation_onboarding_state(self):
        """Thismethodiscalledonthecontrollerrenderingmethodandensuresthattheanimations
            aredisplayedonlyonetime."""
        steps=[
            'base_onboarding_company_state',
            'account_onboarding_invoice_layout_state',
            'sale_onboarding_order_confirmation_state',
            'sale_onboarding_sample_quotation_state',
        ]
        returnself.get_and_update_onbarding_state('sale_quotation_onboarding_state',steps)

    _sql_constraints=[('check_quotation_validity_days','CHECK(quotation_validity_days>0)','QuotationValidityisrequiredandmustbegreaterthan0.')]
