#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importre
fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError


classPrintPreNumberedChecks(models.TransientModel):
    _name='print.prenumbered.checks'
    _description='PrintPre-numberedChecks'

    next_check_number=fields.Char('NextCheckNumber',required=True)

    @api.constrains('next_check_number')
    def_check_next_check_number(self):
        forcheckinself:
            ifcheck.next_check_numberandnotre.match(r'^[0-9]+$',check.next_check_number):
                raiseValidationError(_('NextCheckNumbershouldonlycontainsnumbers.'))

    defprint_checks(self):
        check_number=int(self.next_check_number)
        number_len=len(self.next_check_numberor"")
        payments=self.env['account.payment'].browse(self.env.context['payment_ids'])
        payments.filtered(lambdar:r.state=='draft').action_post()
        payments.filtered(lambdar:r.state=='posted'andnotr.is_move_sent).write({'is_move_sent':True})
        forpaymentinpayments:
            payment.check_number='%0{}d'.format(number_len)%check_number
            check_number+=1
        returnpayments.do_print_checks()
