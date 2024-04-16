#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError


classMailingMailingScheduleDate(models.TransientModel):
    _name='mailing.mailing.schedule.date'
    _description='MassMailingScheduling'

    schedule_date=fields.Datetime(string='Scheduledfor')
    mass_mailing_id=fields.Many2one('mailing.mailing',required=True,ondelete='cascade')

    @api.constrains('schedule_date')
    def_check_schedule_date(self):
        forschedulerinself:
            ifscheduler.schedule_date<fields.Datetime.now():
                raiseValidationError(_('Pleaseselectadateequal/orgreaterthanthecurrentdate.'))

    defset_schedule_date(self):
        self.mass_mailing_id.write({'schedule_date':self.schedule_date,'state':'in_queue'})
