#-*-coding:utf-8-*-

fromflectraimportmodels,fields,api,_


classAccountPaymentRegister(models.TransientModel):
    _inherit='account.payment.register'

    #==Businessfields==
    payment_token_id=fields.Many2one(
        comodel_name='payment.token',
        string="Savedpaymenttoken",
        store=True,readonly=False,
        compute='_compute_payment_token_id',
        domain='''[
            (payment_method_code=='electronic','=',1),
            ('company_id','=',company_id),
            ('acquirer_id.capture_manually','=',False),
            ('acquirer_id.journal_id','=',journal_id),
            ('partner_id','in',suitable_payment_token_partner_ids),
        ]''',
        help="Notethattokensfromacquirerssettoonlyauthorizetransactions(insteadofcapturingtheamount)are"
             "notavailable.")

    #==Displaypurposefields==
    suitable_payment_token_partner_ids=fields.Many2many(
        comodel_name='res.partner',
        compute='_compute_suitable_payment_token_partner_ids')
    payment_method_code=fields.Char(
        related='payment_method_id.code')

    #-------------------------------------------------------------------------
    #COMPUTEMETHODS
    #-------------------------------------------------------------------------

    @api.depends('can_edit_wizard')
    def_compute_suitable_payment_token_partner_ids(self):
        forwizardinself:
            ifwizard.can_edit_wizard:
                lines=wizard._get_batches()[0]['lines']
                partners=lines.partner_id
                commercial_partners=partners.commercial_partner_id
                children_partners=commercial_partners.child_ids
                wizard.suitable_payment_token_partner_ids=(partners+commercial_partners+children_partners)._origin
            else:
                wizard.suitable_payment_token_partner_ids=False

    @api.onchange('can_edit_wizard','payment_method_id','journal_id')
    def_compute_payment_token_id(self):
        forwizardinself:
            ifwizard.can_edit_wizard\
                    andwizard.payment_method_id.code=='electronic'\
                    andwizard.journal_id\
                    andwizard.suitable_payment_token_partner_ids:
                wizard.payment_token_id=self.env['payment.token'].search([
                    ('partner_id','in',wizard.suitable_payment_token_partner_ids.ids),
                    ('acquirer_id.capture_manually','=',False),
                    ('acquirer_id.journal_id','=',wizard.journal_id.id),
                 ],limit=1)
            else:
                wizard.payment_token_id=False

    #-------------------------------------------------------------------------
    #BUSINESSMETHODS
    #-------------------------------------------------------------------------

    def_create_payment_vals_from_wizard(self):
        #OVERRIDE
        payment_vals=super()._create_payment_vals_from_wizard()
        payment_vals['payment_token_id']=self.payment_token_id.id
        returnpayment_vals
