#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models

fromflectra.addons.google_calendar.models.google_syncimportgoogle_calendar_token
fromflectra.addons.google_calendar.utils.google_calendarimportGoogleCalendarService


classResetGoogleAccount(models.TransientModel):
    _name='google.calendar.account.reset'
    _description='GoogleCalendarAccountReset'

    user_id=fields.Many2one('res.users',required=True)
    delete_policy=fields.Selection(
        [('dont_delete',"Leavethemuntouched"),
         ('delete_google',"DeletefromthecurrentGoogleCalendaraccount"),
         ('delete_flectra',"DeletefromFlectra"),
         ('delete_both',"Deletefromboth"),
        ],string="User'sExistingEvents",required=True,default='dont_delete',
        help="Thiswillonlyaffecteventsforwhichtheuseristheowner")
    sync_policy=fields.Selection([
        ('new',"Synchronizeonlynewevents"),
        ('all',"Synchronizeallexistingevents"),
    ],string="NextSynchronization",required=True,default='new')

    defreset_account(self):
        google=GoogleCalendarService(self.env['google.service'])

        events=self.env['calendar.event'].search([
            ('user_id','=',self.user_id.id),
            ('google_id','!=',False)])
        ifself.delete_policyin('delete_google','delete_both'):
            withgoogle_calendar_token(self.user_id)astoken:
                foreventinevents:
                    google.delete(event.google_id,token=token)

        ifself.delete_policyin('delete_flectra','delete_both'):
            events.google_id=False
            events.unlink()

        ifself.sync_policy=='all':
            events.write({
                'google_id':False,
                'need_sync':True,
            })

        self.user_id._set_auth_tokens(False,False,0)
        self.user_id.write({
            'google_calendar_sync_token':False,
            'google_calendar_cal_id':False,
        })
