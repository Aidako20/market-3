#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError


classAccountAnalyticLine(models.Model):
    _inherit='account.analytic.line'

    holiday_id=fields.Many2one("hr.leave",string='LeaveRequest')

    defunlink(self):
        ifany(line.holiday_idforlineinself):
            raiseUserError(_('Youcannotdeletetimesheetlinesattachedtoaleaves.Pleasecanceltheleavesinstead.'))
        returnsuper(AccountAnalyticLine,self).unlink()
