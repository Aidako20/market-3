#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,_


classAccountMove(models.Model):
    _inherit="account.move"

    defbutton_cancel(self):
        forlinself.line_ids:
            ifl.expense_id:
                l.expense_id.refuse_expense(reason=_("PaymentCancelled"))
        returnsuper().button_cancel()

    defbutton_draft(self):
        forlineinself.line_ids:
            ifline.expense_id:
                line.expense_id.sheet_id.write({'state':'post'})
        returnsuper().button_draft()
