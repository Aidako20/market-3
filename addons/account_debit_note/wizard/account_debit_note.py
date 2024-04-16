#-*-coding:utf-8-*-
fromflectraimportmodels,fields,api
fromflectra.tools.translateimport_
fromflectra.exceptionsimportUserError


classAccountDebitNote(models.TransientModel):
    """
    AddDebitNotewizard:whenyouwanttocorrectaninvoicewithapositiveamount.
    OppositeofaCreditNote,butdifferentfromaregularinvoiceasyouneedthelinktotheoriginalinvoice.
    Insomecases,alsousedtocancelCreditNotes
    """
    _name='account.debit.note'
    _description='AddDebitNotewizard'

    move_ids=fields.Many2many('account.move','account_move_debit_move','debit_id','move_id',
                                domain=[('state','=','posted')])
    date=fields.Date(string='DebitNoteDate',default=fields.Date.context_today,required=True)
    reason=fields.Char(string='Reason')
    journal_id=fields.Many2one('account.journal',string='UseSpecificJournal',
                                 help='Ifempty,usesthejournalofthejournalentrytobedebited.')
    copy_lines=fields.Boolean("CopyLines",
                                help="Incaseyouneedtodocorrectionsforeveryline,itcanbeinhandytocopythem. "
                                     "Wewon'tcopythemfordebitnotesfromcreditnotes.")
    #computedfields
    move_type=fields.Char(compute="_compute_from_moves")
    journal_type=fields.Char(compute="_compute_from_moves")
    country_code=fields.Char(related='move_ids.company_id.country_id.code')

    @api.model
    defdefault_get(self,fields):
        res=super(AccountDebitNote,self).default_get(fields)
        move_ids=self.env['account.move'].browse(self.env.context['active_ids'])ifself.env.context.get('active_model')=='account.move'elseself.env['account.move']
        ifany(move.state!="posted"formoveinmove_ids):
            raiseUserError(_('Youcanonlydebitpostedmoves.'))
        res['move_ids']=[(6,0,move_ids.ids)]
        returnres

    @api.depends('move_ids')
    def_compute_from_moves(self):
        forrecordinself:
            move_ids=record.move_ids
            record.move_type=move_ids[0].move_typeiflen(move_ids)==1ornotany(m.move_type!=move_ids[0].move_typeforminmove_ids)elseFalse
            record.journal_type=record.move_typein['in_refund','in_invoice']and'purchase'or'sale'

    def_prepare_default_values(self,move):
        ifmove.move_typein('in_refund','out_refund'):
            type='in_invoice'ifmove.move_type=='in_refund'else'out_invoice'
        else:
            type=move.move_type
        default_values={
                'ref':'%s,%s'%(move.name,self.reason)ifself.reasonelsemove.name,
                'date':self.dateormove.date,
                'invoice_date':move.is_invoice(include_receipts=True)and(self.dateormove.date)orFalse,
                'journal_id':self.journal_idandself.journal_id.idormove.journal_id.id,
                'invoice_payment_term_id':None,
                'debit_origin_id':move.id,
                'move_type':type,
            }
        ifnotself.copy_linesormove.move_typein[('in_refund','out_refund')]:
            default_values['line_ids']=[(5,0,0)]
        returndefault_values

    defcreate_debit(self):
        self.ensure_one()
        new_moves=self.env['account.move']
        formoveinself.move_ids.with_context(include_business_fields=True):#copysale/purchaselinks
            default_values=self._prepare_default_values(move)
            new_move=move.copy(default=default_values)
            move_msg=_(
                "Thisdebitnotewascreatedfrom:")+"<ahref=#data-oe-model=account.movedata-oe-id=%d>%s</a>"%(
                       move.id,move.name)
            new_move.message_post(body=move_msg)
            new_moves|=new_move

        action={
            'name':_('DebitNotes'),
            'type':'ir.actions.act_window',
            'res_model':'account.move',
            'context':{'default_move_type':default_values['move_type']},
        }
        iflen(new_moves)==1:
            action.update({
                'view_mode':'form',
                'res_id':new_moves.id,
            })
        else:
            action.update({
                'view_mode':'tree,form',
                'domain':[('id','in',new_moves.ids)],
            })
        returnaction
