#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError


classAccountInvoiceSend(models.TransientModel):
    _name='account.invoice.send'
    _inherit='account.invoice.send'
    _description='AccountInvoiceSend'

    partner_id=fields.Many2one('res.partner',compute='_get_partner',string='Partner')
    snailmail_is_letter=fields.Boolean('SendbyPost',
        help='AllowstosendthedocumentbySnailmail(conventionalpostingdeliveryservice)',
        default=lambdaself:self.env.company.invoice_is_snailmail)
    snailmail_cost=fields.Float(string='Stamp(s)',compute='_compute_snailmail_cost',readonly=True)
    invalid_addresses=fields.Integer('InvalidAddressesCount',compute='_compute_invalid_addresses')
    invalid_invoice_ids=fields.Many2many('account.move',string='InvalidAddresses',compute='_compute_invalid_addresses')

    @api.depends('invoice_ids')
    def_compute_invalid_addresses(self):
        forwizardinself:
            invalid_invoices=wizard.invoice_ids.filtered(lambdai:noti.partner_idornotself.env['snailmail.letter']._is_valid_address(i.partner_id))
            wizard.invalid_invoice_ids=invalid_invoices
            wizard.invalid_addresses=len(invalid_invoices)

    @api.depends('invoice_ids')
    def_get_partner(self):
        self.partner_id=self.env['res.partner']
        forwizardinself:
            ifwizard.invoice_idsandlen(wizard.invoice_ids)==1:
                wizard.partner_id=wizard.invoice_ids.partner_id.id

    @api.depends('snailmail_is_letter')
    def_compute_snailmail_cost(self):
        forwizardinself:
            wizard.snailmail_cost=len(wizard.invoice_ids.ids)

    defsnailmail_print_action(self):
        self.ensure_one()
        letters=self.env['snailmail.letter']
        forinvoiceinself.invoice_ids:
            letter=self.env['snailmail.letter'].create({
                'partner_id':invoice.partner_id.id,
                'model':'account.move',
                'res_id':invoice.id,
                'user_id':self.env.user.id,
                'company_id':invoice.company_id.id,
                'report_template':self.env.ref('account.account_invoices').id
            })
            letters|=letter

        self.invoice_ids.filtered(lambdainv:notinv.is_move_sent).write({'is_move_sent':True})
        iflen(self.invoice_ids)==1:
            letters._snailmail_print()
        else:
            letters._snailmail_print(immediate=False)

    defsend_and_print_action(self):
        ifself.snailmail_is_letter:
            ifself.env['snailmail.confirm.invoice'].show_warning():
                wizard=self.env['snailmail.confirm.invoice'].create({'model_name':_('Invoice'),'invoice_send_id':self.id})
                returnwizard.action_open()
            self._print_action()
        returnself.send_and_print()
    
    def_print_action(self):
        ifnotself.snailmail_is_letter:
            return

        ifself.invalid_addressesandself.composition_mode=="mass_mail":
            self.notify_invalid_addresses()
        self.snailmail_print_action()

    defsend_and_print(self):
        res=super(AccountInvoiceSend,self).send_and_print_action()
        returnres

    defnotify_invalid_addresses(self):
        self.ensure_one()
        self.env['bus.bus'].sendone(
            (self._cr.dbname,'res.partner',self.env.user.partner_id.id),
            {'type':'snailmail_invalid_address','title':_("InvalidAddresses"),
            'message':_("%softheselectedinvoice(s)hadaninvalidaddressandwerenotsent",self.invalid_addresses)}
        )

    definvalid_addresses_action(self):
        return{
            'name':_('InvalidAddresses'),
            'type':'ir.actions.act_window',
            'view_mode':'kanban,tree,form',
            'res_model':'account.move',
            'domain':[('id','in',self.mapped('invalid_invoice_ids').ids)],
        }
