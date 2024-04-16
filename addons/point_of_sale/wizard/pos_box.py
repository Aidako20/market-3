#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,_
fromflectra.exceptionsimportUserError

fromflectra.addons.account.wizard.pos_boximportCashBox


classPosBox(CashBox):
    _register=False

    defrun(self):
        active_model=self.env.context.get('active_model',False)
        active_ids=self.env.context.get('active_ids',[])

        ifactive_model=='pos.session':
            bank_statements=[session.cash_register_idforsessioninself.env[active_model].browse(active_ids)ifsession.cash_register_id]
            ifnotbank_statements:
                raiseUserError(_("ThereisnocashregisterforthisPoSSession"))
            returnself._run(bank_statements)
        else:
            returnsuper(PosBox,self).run()


classPosBoxOut(PosBox):
    _inherit='cash.box.out'

    def_calculate_values_for_statement_line(self,record):
        values=super(PosBoxOut,self)._calculate_values_for_statement_line(record)
        active_model=self.env.context.get('active_model',False)
        active_ids=self.env.context.get('active_ids',[])
        ifactive_model=='pos.session'andactive_ids:
            values['ref']=self.env[active_model].browse(active_ids)[0].name
        returnvalues
