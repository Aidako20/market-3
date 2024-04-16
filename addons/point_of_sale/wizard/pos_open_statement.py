#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,_
fromflectra.exceptionsimportUserError


classPosOpenStatement(models.TransientModel):
    _name='pos.open.statement'
    _description='PointofSaleOpenStatement'

    defopen_statement(self):
        self.ensure_one()
        BankStatement=self.env['account.bank.statement']
        journals=self.env['account.journal'].search([('journal_user','=',True)])
        ifnotjournals:
            raiseUserError(_('Youhavetodefinewhichpaymentmethodmustbeavailableinthepointofsalebyreusingexistingbankandcashthrough"Accounting/Configuration/Journals/Journals".Selectajournalandcheckthefield"PoSPaymentMethod"fromthe"PointofSale"tab.Youcanalsocreatenewpaymentmethodsdirectlyfrommenu"PoSBackend/Configuration/PaymentMethods".'))

        forjournalinjournals:
            ifjournal.sequence_id:
                number=journal.sequence_id.next_by_id()
            else:
                raiseUserError(_("Nosequencedefinedonthejournal"))
            BankStatement+=BankStatement.create({'journal_id':journal.id,'user_id':self.env.uid,'name':number})

        tree_id=self.env.ref('account.view_bank_statement_tree').id
        form_id=self.env.ref('account.view_bank_statement_form').id
        search_id=self.env.ref('account.view_bank_statement_search').id

        return{
            'type':'ir.actions.act_window',
            'name':_('ListofCashRegisters'),
            'view_mode':'tree,form',
            'res_model':'account.bank.statement',
            'domain':str([('id','in',BankStatement.ids)]),
            'views':[(tree_id,'tree'),(form_id,'form')],
            'search_view_id':search_id,
        }
