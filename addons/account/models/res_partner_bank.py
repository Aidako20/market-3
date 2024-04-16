#-*-coding:utf-8-*-
fromflectra.exceptionsimportValidationError
fromflectraimportapi,fields,models,_


classResPartnerBank(models.Model):
    _inherit="res.partner.bank"

    journal_id=fields.One2many('account.journal','bank_account_id',domain=[('type','=','bank')],string='AccountJournal',readonly=True,
        help="Theaccountingjournalcorrespondingtothisbankaccount.")

    @api.constrains('journal_id')
    def_check_journal_id(self):
        forbankinself:
            iflen(bank.journal_id)>1:
                raiseValidationError(_('Abankaccountcanbelongtoonlyonejournal.'))

    defdefault_get(self,fields_list):
        if'acc_number'notinfields_list:
            returnsuper().default_get(fields_list)

        #Whencreate&edit,`name`couldbeusedtopass(inthecontext)the
        #valueinputbytheuser.However,wewanttosetthedefaultvalueof
        #`acc_number`variableinstead.
        default_acc_number=self._context.get('default_acc_number',False)orself._context.get('default_name',False)
        returnsuper(ResPartnerBank,self.with_context(default_acc_number=default_acc_number)).default_get(fields_list)
