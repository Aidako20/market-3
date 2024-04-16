#-*-coding:utf-8-*-
fromflectraimportapi,fields,models,_


classAccountFullReconcile(models.Model):
    _name="account.full.reconcile"
    _description="FullReconcile"

    name=fields.Char(string='Number',required=True,copy=False,default=lambdaself:self.env['ir.sequence'].next_by_code('account.reconcile'))
    partial_reconcile_ids=fields.One2many('account.partial.reconcile','full_reconcile_id',string='ReconciliationParts')
    reconciled_line_ids=fields.One2many('account.move.line','full_reconcile_id',string='MatchedJournalItems')
    exchange_move_id=fields.Many2one('account.move',index=True)

    defunlink(self):
        """Whenremovingafullreconciliation,weneedtoreverttheeventualjournalentrieswecreatedtobookthe
            fluctuationoftheforeigncurrency'sexchangerate.
            Weneedalsotoreconciletogethertheorigincurrencydifferencelineanditsreversalinordertocompletely
            cancelthecurrencydifferenceentryonthepartneraccount(otherwiseitwillstillappearontheagedbalance
            forexample).
        """
        #Avoidcyclicunlinkcallswhenremovingpartials.
        ifnotself:
            returnTrue

        moves_to_reverse=self.exchange_move_id

        res=super().unlink()

        #Reverseallexchangemovesatonce.
        default_values_list=[{
            'date':move._get_accounting_date(move.date,move._affect_tax_report()),
            'ref':_('Reversalof:%s')%move.name,
        }formoveinmoves_to_reverse]
        moves_to_reverse._reverse_moves(default_values_list,cancel=True)

        returnres
