#-*-coding:utf-8-*-
fromflectraimportmodels,fields,api
fromflectra.tools.translateimport_
fromflectra.exceptionsimportUserError


classAccountMoveReversal(models.TransientModel):
    """
    Accountmovereversalwizard,itcancelanaccountmovebyreversingit.
    """
    _name='account.move.reversal'
    _description='AccountMoveReversal'
    _check_company_auto=True

    move_ids=fields.Many2many('account.move','account_move_reversal_move','reversal_id','move_id',domain=[('state','=','posted')])
    new_move_ids=fields.Many2many('account.move','account_move_reversal_new_move','reversal_id','new_move_id')
    date_mode=fields.Selection(selection=[
            ('custom','Specific'),
            ('entry','JournalEntryDate')
    ],required=True,default='custom')
    date=fields.Date(string='Reversaldate',default=fields.Date.context_today)
    reason=fields.Char(string='Reason')
    refund_method=fields.Selection(selection=[
            ('refund','PartialRefund'),
            ('cancel','FullRefund'),
            ('modify','Fullrefundandnewdraftinvoice')
        ],string='CreditMethod',required=True,
        help='Choosehowyouwanttocreditthisinvoice.Youcannot"modify"nor"cancel"iftheinvoiceisalreadyreconciled.')
    journal_id=fields.Many2one('account.journal',string='UseSpecificJournal',help='Ifempty,usesthejournalofthejournalentrytobereversed.',check_company=True)
    company_id=fields.Many2one('res.company',required=True,readonly=True)
    country_code=fields.Char(related='company_id.country_id.code')

    #computedfields
    residual=fields.Monetary(compute="_compute_from_moves")
    currency_id=fields.Many2one('res.currency',compute="_compute_from_moves")
    move_type=fields.Char(compute="_compute_from_moves")

    @api.model
    defdefault_get(self,fields):
        res=super(AccountMoveReversal,self).default_get(fields)
        move_ids=self.env['account.move'].browse(self.env.context['active_ids'])ifself.env.context.get('active_model')=='account.move'elseself.env['account.move']

        ifany(move.state!="posted"formoveinmove_ids):
            raiseUserError(_('Youcanonlyreversepostedmoves.'))
        if'company_id'infields:
            res['company_id']=move_ids.company_id.idorself.env.company.id
        if'move_ids'infields:
            res['move_ids']=[(6,0,move_ids.ids)]
        if'refund_method'infields:
            res['refund_method']=(len(move_ids)>1ormove_ids.move_type=='entry')and'cancel'or'refund'
        returnres

    @api.depends('move_ids')
    def_compute_from_moves(self):
        forrecordinself:
            move_ids=record.move_ids._origin
            record.residual=len(move_ids)==1andmove_ids.amount_residualor0
            record.currency_id=len(move_ids.currency_id)==1andmove_ids.currency_idorFalse
            record.move_type=move_ids.move_typeiflen(move_ids)==1else(any(move.move_typein('in_invoice','out_invoice')formoveinmove_ids)and'some_invoice'orFalse)

    def_prepare_default_reversal(self,move):
        reverse_date=self.dateifself.date_mode=='custom'elsemove.date
        return{
            'ref':_('Reversalof:%(move_name)s,%(reason)s',move_name=move.name,reason=self.reason)
                   ifself.reason
                   else_('Reversalof:%s',move.name),
            'date':reverse_date,
            'invoice_date':move.is_invoice(include_receipts=True)and(self.dateormove.date)orFalse,
            'journal_id':self.journal_idandself.journal_id.idormove.journal_id.id,
            'invoice_payment_term_id':None,
            'invoice_user_id':move.invoice_user_id.id,
            'auto_post':Trueifreverse_date>fields.Date.context_today(self)elseFalse,
        }

    def_reverse_moves_post_hook(self,moves):
        #DEPRECATED:TOREMOVEINMASTER
        return

    defreverse_moves(self):
        self.ensure_one()
        moves=self.move_ids

        #Createdefaultvalues.
        default_values_list=[]
        formoveinmoves:
            default_values_list.append(self._prepare_default_reversal(move))

        batches=[
            [self.env['account.move'],[],True],  #Movestobecancelledbythereverses.
            [self.env['account.move'],[],False], #Others.
        ]
        formove,default_valsinzip(moves,default_values_list):
            is_auto_post=bool(default_vals.get('auto_post'))
            is_cancel_needed=notis_auto_postandself.refund_methodin('cancel','modify')
            batch_index=0ifis_cancel_neededelse1
            batches[batch_index][0]|=move
            batches[batch_index][1].append(default_vals)

        #Handlereversemethod.
        moves_to_redirect=self.env['account.move']
        formoves,default_values_list,is_cancel_neededinbatches:
            new_moves=moves._reverse_moves(default_values_list,cancel=is_cancel_needed)

            ifself.refund_method=='modify':
                moves_vals_list=[]
                formoveinmoves.with_context(include_business_fields=True):
                    moves_vals_list.append(move.copy_data({'date':self.dateifself.date_mode=='custom'elsemove.date})[0])
                new_moves=self.env['account.move'].create(moves_vals_list)

            moves_to_redirect|=new_moves

        self.new_move_ids=moves_to_redirect

        #Createaction.
        action={
            'name':_('ReverseMoves'),
            'type':'ir.actions.act_window',
            'res_model':'account.move',
        }
        iflen(moves_to_redirect)==1:
            action.update({
                'view_mode':'form',
                'res_id':moves_to_redirect.id,
                'context':{'default_move_type': moves_to_redirect.move_type},
            })
        else:
            action.update({
                'view_mode':'tree,form',
                'domain':[('id','in',moves_to_redirect.ids)],
            })
            iflen(set(moves_to_redirect.mapped('move_type')))==1:
                action['context']={'default_move_type': moves_to_redirect.mapped('move_type').pop()}
        returnaction
