#-*-coding:utf-8-*-

fromflectraimportmodels


classAccountPaymentRegister(models.TransientModel):
    _inherit='account.payment.register'

    def_create_payment_vals_from_wizard(self):
        vals=super()._create_payment_vals_from_wizard()
        #Makesuretheaccountmovelinkedtogeneratedpayment
        #belongstotheexpectedsalesteam
        #team_idfieldonaccount.paymentcomesfromthe`_inherits`onaccount.movemodel
        vals.update({'team_id':self.line_ids.move_id[0].team_id.id})
        returnvals
