#-*-coding:utf-8-*-

fromflectraimportmodels,fields,api,_


classAccountPaymentRegister(models.TransientModel):
    _inherit='account.payment.register'

    #-------------------------------------------------------------------------
    #BUSINESSMETHODS
    #-------------------------------------------------------------------------
    
    @api.model
    def_get_line_batch_key(self,line):
        #OVERRIDEtosetthebankaccountdefinedontheemployee
        res=super()._get_line_batch_key(line)
        expense_sheet=self.env['hr.expense.sheet'].search([('payment_mode','=','own_account'),('account_move_id','in',line.move_id.ids)])
        ifexpense_sheetandnotline.move_id.partner_bank_id:
            res['partner_bank_id']=expense_sheet.employee_id.sudo().bank_account_id.idorline.partner_id.bank_idsandline.partner_id.bank_ids.ids[0]
        returnres

    def_init_payments(self,to_process,edit_mode=False):
        #OVERRIDE
        payments=super()._init_payments(to_process,edit_mode=edit_mode)
        forpayment,valsinzip(payments,to_process):
            expenses=vals['batch']['lines'].expense_id
            ifexpenses:
                payment.line_ids.write({'expense_id':expenses[0].id})
        returnpayments

    def_reconcile_payments(self,to_process,edit_mode=False):
        #OVERRIDE
        res=super()._reconcile_payments(to_process,edit_mode=edit_mode)
        forvalsinto_process:
            expense_sheets=vals['batch']['lines'].expense_id.sheet_id
            forexpense_sheetinexpense_sheets:
                ifexpense_sheet.currency_id.is_zero(expense_sheet.amount_residual):
                    expense_sheet.state='done'
        returnres
