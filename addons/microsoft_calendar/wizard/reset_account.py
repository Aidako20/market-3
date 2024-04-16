#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models

fromflectra.addons.microsoft_calendar.models.microsoft_syncimportmicrosoft_calendar_token


classResetMicrosoftAccount(models.TransientModel):
    _name='microsoft.calendar.account.reset'
    _description='MicrosoftCalendarAccountReset'

    user_id=fields.Many2one('res.users',required=True)
    delete_policy=fields.Selection(
        [('dont_delete',"Leavethemuntouched"),
         ('delete_microsoft',"DeletefromthecurrentMicrosoftCalendaraccount"),
         ('delete_flectra',"DeletefromFlectra"),
         ('delete_both',"Deletefromboth"),
    ],string="User'sExistingEvents",required=True,default='dont_delete',
    help="Thiswillonlyaffecteventsforwhichtheuseristheowner")
    sync_policy=fields.Selection([
        ('new',"Synchronizeonlynewevents"),
        ('all',"Synchronizeallexistingevents"),
    ],string="NextSynchronization",required=True,default='new')

    defreset_account(self):
        microsoft=self.env["calendar.event"]._get_microsoft_service()

        events=self.env['calendar.event'].search([
            ('user_id','=',self.user_id.id),
            ('ms_universal_event_id','!=',False)])
        ifself.delete_policyin('delete_microsoft','delete_both'):
            withmicrosoft_calendar_token(self.user_id)astoken:
                foreventinevents:
                    microsoft.delete(event.ms_universal_event_id,token=token)

        ifself.delete_policyin('delete_flectra','delete_both'):
            events.microsoft_id=False
            events.unlink()

        ifself.sync_policy=='all':
            events.write({
                'microsoft_id':False,
                'need_sync_m':True,
            })

        self.user_id._set_microsoft_auth_tokens(False,False,0)
        self.user_id.write({
            'microsoft_calendar_sync_token':False,
        })
