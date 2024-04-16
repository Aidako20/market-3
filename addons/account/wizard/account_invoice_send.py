#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.addons.mail.wizard.mail_compose_messageimport_reopen
fromflectra.exceptionsimportUserError
fromflectra.tools.miscimportget_lang


classAccountInvoiceSend(models.TransientModel):
    _name='account.invoice.send'
    _inherits={'mail.compose.message':'composer_id'}
    _description='AccountInvoiceSend'

    is_email=fields.Boolean('Email',default=lambdaself:self.env.company.invoice_is_email)
    invoice_without_email=fields.Text(compute='_compute_invoice_without_email',string='invoice(s)thatwillnotbesent')
    is_print=fields.Boolean('Print',default=lambdaself:self.env.company.invoice_is_print)
    printed=fields.Boolean('IsPrinted',default=False)
    invoice_ids=fields.Many2many('account.move','account_move_account_invoice_send_rel',string='Invoices')
    composer_id=fields.Many2one('mail.compose.message',string='Composer',required=True,ondelete='cascade')
    template_id=fields.Many2one(
        'mail.template','Usetemplate',index=True,
        domain="[('model','=','account.move')]"
        )

    @api.model
    defdefault_get(self,fields):
        res=super(AccountInvoiceSend,self).default_get(fields)
        res_ids=self._context.get('active_ids')

        invoices=self.env['account.move'].browse(res_ids).filtered(lambdamove:move.is_invoice(include_receipts=True))
        ifnotinvoices:
            raiseUserError(_("Youcanonlysendinvoices."))

        composer=self.env['mail.compose.message'].create({
            'composition_mode':'comment'iflen(res_ids)==1else'mass_mail',
        })
        res.update({
            'invoice_ids':res_ids,
            'composer_id':composer.id,
        })
        returnres

    @api.onchange('invoice_ids')
    def_compute_composition_mode(self):
        forwizardinself:
            wizard.composer_id.composition_mode='comment'iflen(wizard.invoice_ids)==1else'mass_mail'

    @api.onchange('template_id')
    defonchange_template_id(self):
        forwizardinself:
            ifwizard.composer_id:
                wizard.composer_id.template_id=wizard.template_id.id
                wizard._compute_composition_mode()
                wizard.composer_id.onchange_template_id_wrapper()

    @api.onchange('is_email')
    defonchange_is_email(self):
        ifself.is_email:
            res_ids=self._context.get('active_ids')
            ifnotself.composer_id:
                self.composer_id=self.env['mail.compose.message'].create({
                    'composition_mode':'comment'iflen(res_ids)==1else'mass_mail',
                    'template_id':self.template_id.id
                })
            else:
                self.composer_id.composition_mode='comment'iflen(res_ids)==1else'mass_mail'
                self.composer_id.template_id=self.template_id.id
                self._compute_composition_mode()
            self.composer_id.onchange_template_id_wrapper()

    @api.onchange('is_email')
    def_compute_invoice_without_email(self):
        forwizardinself:
            ifwizard.is_emailandlen(wizard.invoice_ids)>1:
                invoices=self.env['account.move'].search([
                    ('id','in',self.env.context.get('active_ids')),
                    ('partner_id.email','=',False)
                ])
                ifinvoices:
                    wizard.invoice_without_email="%s\n%s"%(
                        _("Thefollowinginvoice(s)willnotbesentbyemail,becausethecustomersdon'thaveemailaddress."),
                        "\n".join([i.nameforiininvoices])
                        )
                else:
                    wizard.invoice_without_email=False
            else:
                wizard.invoice_without_email=False

    def_send_email(self):
        ifself.is_email:
            #with_context:wedon'twanttoreimportthefilewejustexported.
            self.composer_id.with_context(no_new_invoice=True,mail_notify_author=self.env.user.partner_idinself.composer_id.partner_ids).send_mail()
            ifself.env.context.get('mark_invoice_as_sent'):
                #Salesmansendpostedinvoice,withouttherighttowrite
                #buttheyshouldhavetherighttochangethisflag
                self.mapped('invoice_ids').sudo().write({'is_move_sent':True})

    def_print_document(self):
        """tooverrideforeachtypeofmodelsthatwillusethiscomposer."""
        self.ensure_one()
        action=self.invoice_ids.action_invoice_print()
        action.update({'close_on_report_download':True})
        returnaction

    defsend_and_print_action(self):
        self.ensure_one()
        #Sendthemailsinthecorrectlanguagebysplittingtheidsperlang.
        #Thisshouldideallybefixedinmail_compose_message,sowhenafixismadetherethiswholecommitshouldbereverted.
        #basicallyself.body(whichcouldbemanuallyedited)extractsself.template_id,
        #whichisthennottranslatedforeachcustomer.
        ifself.composition_mode=='mass_mail'andself.template_id:
            active_ids=self.env.context.get('active_ids',self.res_id)
            active_records=self.env[self.model].browse(active_ids)
            langs=active_records.mapped('partner_id.lang')
            default_lang=get_lang(self.env)
            forlangin(set(langs)or[default_lang]):
                active_ids_lang=active_records.filtered(lambdar:r.partner_id.lang==lang).ids
                self_lang=self.with_context(active_ids=active_ids_lang,lang=lang)
                self_lang.onchange_template_id()
                self_lang._send_email()
        else:
            self._send_email()
        ifself.is_print:
            returnself._print_document()
        return{'type':'ir.actions.act_window_close'}

    defsave_as_template(self):
        self.ensure_one()
        self.composer_id.save_as_template()
        self.template_id=self.composer_id.template_id.id
        action=_reopen(self,self.id,self.model,context=self._context)
        action.update({'name':_('SendInvoice')})
        returnaction
