fromflectraimportmodels,fields,api,_
fromflectra.exceptionsimportUserError

classCashBox(models.TransientModel):
    _register=False

    name=fields.Char(string='Reason',required=True)
    #Attention,wedon'tsetadomain,becausethereisajournal_typekey
    #inthecontextoftheaction
    amount=fields.Float(string='Amount',digits=0,required=True)

    defrun(self):
        context=dict(self._contextor{})
        active_model=context.get('active_model',False)
        active_ids=context.get('active_ids',[])

        records=self.env[active_model].browse(active_ids)

        returnself._run(records)

    def_run(self,records):
        forboxinself:
            forrecordinrecords:
                ifnotrecord.journal_id:
                    raiseUserError(_("Pleasecheckthatthefield'Journal'issetontheBankStatement"))
                ifnotrecord.journal_id.company_id.transfer_account_id:
                    raiseUserError(_("Pleasecheckthatthefield'TransferAccount'issetonthecompany."))
                box._create_bank_statement_line(record)
        return{}

    def_create_bank_statement_line(self,record):
        forboxinself:
            ifrecord.state=='confirm':
                raiseUserError(_("Youcannotput/takemoneyin/outforabankstatementwhichisclosed."))
            values=box._calculate_values_for_statement_line(record)
            self.env['account.bank.statement.line'].sudo().create(values)


classCashBoxOut(CashBox):
    _name='cash.box.out'
    _description='CashBoxOut'

    def_calculate_values_for_statement_line(self,record):
        ifnotrecord.journal_id.company_id.transfer_account_id:
            raiseUserError(_("Youhavetodefinean'InternalTransferAccount'inyourcashregister'sjournal."))
        amount=self.amountor0.0
        return{
            'date':record.date,
            'statement_id':record.id,
            'journal_id':record.journal_id.id,
            'amount':amount,
            'payment_ref':self.name,
        }
