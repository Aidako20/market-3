#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api,_
fromflectra.modules.moduleimportget_resource_path
importbase64

classAccountTourUploadBill(models.TransientModel):
    _name='account.tour.upload.bill'
    _description='Accounttouruploadbill'
    _inherits={'mail.compose.message':'composer_id'}

    composer_id=fields.Many2one('mail.compose.message',string='Composer',required=True,ondelete='cascade')

    selection=fields.Selection(
        selection=lambdaself:self._selection_values(),
        default="sample"
    )

    sample_bill_preview=fields.Binary(
        readonly=True,
        compute='_compute_sample_bill_image'
    )

    def_selection_values(self):
        journal_alias=self.env['account.journal']\
            .search([('type','=','purchase'),('company_id','=',self.env.company.id)],limit=1)

        return[('sample',_('Tryasamplevendorbill')),
                ('upload',_('Uploadyourownbill')),
                ('email',_('Orsendabillto%s@%s',journal_alias.alias_name,journal_alias.alias_domain))]

    def_compute_sample_bill_image(self):
        """Retrievesamplebillwithfacturxtospeeduponboarding"""
        try:
            path=get_resource_path('account_edi_facturx','data/files','Invoice.pdf')
            self.sample_bill_preview=base64.b64encode(open(path,'rb').read())ifpathelseFalse
        except(IOError,OSError):
            self.sample_bill_preview=False
        return

    def_action_list_view_bill(self,bill_ids=[]):
        context=dict(self._context)
        context['default_move_type']='in_invoice'
        return{
            'name':_('GeneratedDocuments'),
            'domain':[('id','in',bill_ids)],
            'view_mode':'tree,form',
            'res_model':'account.move',
            'views':[[False,"tree"],[False,"form"]],
            'type':'ir.actions.act_window',
            'context':context
        }

    defapply(self):
        purchase_journal=self.env['account.journal'].search([('type','=','purchase')],limit=1)
        ifself.selection=='upload':
            returnpurchase_journal.with_context(default_journal_id=purchase_journal.id,default_move_type='in_invoice').create_invoice_from_attachment(attachment_ids=self.attachment_ids.ids)
        elifself.selection=='sample':
            attachment=self.env['ir.attachment'].create({
                'type':'binary',
                'name':'INV/2020/0011.pdf',
                'res_model':'mail.compose.message',
                'datas':self.sample_bill_preview,
            })
            bill_action=purchase_journal.with_context(default_journal_id=purchase_journal.id,default_move_type='in_invoice').create_invoice_from_attachment(attachment.ids)
            bill=self.env['account.move'].browse(bill_action['res_id'])
            bill.write({
                    'partner_id':self.env.ref('base.main_partner').id,
                    'ref':'INV/2020/0011'
                })
            returnself._action_list_view_bill(bill.ids)
        else:
            email_alias='%s@%s'%(purchase_journal.alias_name,purchase_journal.alias_domain)
            new_wizard=self.env['account.tour.upload.bill.email.confirm'].create({'email_alias':email_alias})
            view_id=self.env.ref('account.account_tour_upload_bill_email_confirm').id

            return{
                'type':'ir.actions.act_window',
                'name':_('Confirm'),
                'view_mode':'form',
                'res_model':'account.tour.upload.bill.email.confirm',
                'target':'new',
                'res_id':new_wizard.id,
                'views':[[view_id,'form']],
            }


classAccountTourUploadBillEmailConfirm(models.TransientModel):
    _name='account.tour.upload.bill.email.confirm'
    _description='Accounttouruploadbillemailconfirm'

    email_alias=fields.Char(readonly=True)

    defapply(self):
        purchase_journal=self.env['account.journal'].search([('type','=','purchase')],limit=1)
        bill_ids=self.env['account.move'].search([('journal_id','=',purchase_journal.id)]).ids
        returnself.env['account.tour.upload.bill']._action_list_view_bill(bill_ids)
