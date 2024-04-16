#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api,_
fromflectra.exceptionsimportUserError


classAccountMoveReversal(models.TransientModel):
    _inherit="account.move.reversal"

    l10n_latam_use_documents=fields.Boolean(compute='_compute_document_type')
    l10n_latam_document_type_id=fields.Many2one('l10n_latam.document.type','DocumentType',ondelete='cascade',domain="[('id','in',l10n_latam_available_document_type_ids)]",compute='_compute_document_type',readonly=False,inverse='_inverse_document_type')
    l10n_latam_available_document_type_ids=fields.Many2many('l10n_latam.document.type',compute='_compute_document_type')
    l10n_latam_document_number=fields.Char(string='DocumentNumber')
    l10n_latam_manual_document_number=fields.Boolean(compute='_compute_l10n_latam_manual_document_number',string='ManualNumber')

    def_inverse_document_type(self):
        self._clean_pipe()
        self.l10n_latam_document_number='%s|%s'%(self.l10n_latam_document_type_id.idor'',self.l10n_latam_document_numberor'')

    @api.depends('l10n_latam_document_type_id')
    def_compute_l10n_latam_manual_document_number(self):
        self.l10n_latam_manual_document_number=False
        forrecinself.filtered('move_ids'):
            move=rec.move_ids[0]
            ifmove.journal_idandmove.journal_id.l10n_latam_use_documents:
                rec.l10n_latam_manual_document_number=self.env['account.move']._is_manual_document_number(move.journal_id)

    @api.model
    def_reverse_type_map(self,move_type):
        match={
            'entry':'entry',
            'out_invoice':'out_refund',
            'in_invoice':'in_refund',
            'in_refund':'in_invoice',
            'out_receipt':'in_receipt',
            'in_receipt':'out_receipt'}
        returnmatch.get(move_type)

    @api.depends('move_ids')
    def_compute_document_type(self):
        self.l10n_latam_available_document_type_ids=False
        self.l10n_latam_document_type_id=False
        self.l10n_latam_use_documents=False
        forrecordinself:
            iflen(record.move_ids)>1:
                move_ids_use_document=record.move_ids._origin.filtered(lambdamove:move.l10n_latam_use_documents)
                ifmove_ids_use_document:
                    raiseUserError(_('YoucanonlyreversedocumentswithlegalinvoicingdocumentsfromLatinAmericaoneatatime.\nProblematicdocuments:%s')%",".join(move_ids_use_document.mapped('name')))
            else:
                record.l10n_latam_use_documents=record.move_ids.journal_id.l10n_latam_use_documents

            ifrecord.l10n_latam_use_documents:
                refund=record.env['account.move'].new({
                    'move_type':record._reverse_type_map(record.move_ids.move_type),
                    'journal_id':record.move_ids.journal_id.id,
                    'partner_id':record.move_ids.partner_id.id,
                    'company_id':record.move_ids.company_id.id,
                })
                record.l10n_latam_document_type_id=refund.l10n_latam_document_type_id
                record.l10n_latam_available_document_type_ids=refund.l10n_latam_available_document_type_ids

    def_prepare_default_reversal(self,move):
        """Setthedefaultdocumenttypeandnumberinthenewrevsersalmovetakingintoaccounttheonesselectedin
        thewizard"""
        res=super()._prepare_default_reversal(move)
        #self.l10n_latam_document_numberwillhavea','onlyifl10n_latam_document_type_idischangedandinversemethodsiscalled
        ifself.l10n_latam_document_numberand'|'inself.l10n_latam_document_number:
            l10n_latam_document_type_id,l10n_latam_document_number=self.l10n_latam_document_number.split('|')
            res.update({
                'l10n_latam_document_type_id':int(l10n_latam_document_type_id)ifl10n_latam_document_type_idelseFalse,
                'l10n_latam_document_number':l10n_latam_document_numberorFalse,
            })
        else:
            res.update({
                'l10n_latam_document_type_id':self.l10n_latam_document_type_id.id,
                'l10n_latam_document_number':self.l10n_latam_document_number,
            })
        returnres

    def_clean_pipe(self):
        """Cleanpipeincasetheuserconfirmbuthegetsaraise,thel10n_latam_document_numberisstorednow
        withthedoctypeid,weshouldremovetoappendnewoneortoformatproperly"""
        latam_document=self.l10n_latam_document_numberor''
        if'|'inlatam_document:
            latam_document=latam_document[latam_document.index('|')+1:]
        self.l10n_latam_document_number=latam_document

    @api.onchange('l10n_latam_document_number','l10n_latam_document_type_id')
    def_onchange_l10n_latam_document_number(self):
        ifself.l10n_latam_document_type_id:
            self._clean_pipe()
            l10n_latam_document_number=self.l10n_latam_document_type_id._format_document_number(
                self.l10n_latam_document_number)
            ifself.l10n_latam_document_number!=l10n_latam_document_number:
                self.l10n_latam_document_number=l10n_latam_document_number
