#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimporttimedelta


fromflectraimportapi,fields,models,_


classUser(models.Model):
    _inherit='res.users'

    microsoft_calendar_rtoken=fields.Char('MicrosoftRefreshToken',copy=False,groups="base.group_system")
    microsoft_calendar_token=fields.Char('MicrosoftUsertoken',copy=False,groups="base.group_system")
    microsoft_calendar_token_validity=fields.Datetime('MicrosoftTokenValidity',copy=False)

    def_set_microsoft_auth_tokens(self,access_token,refresh_token,ttl):
        self.write({
            'microsoft_calendar_rtoken':refresh_token,
            'microsoft_calendar_token':access_token,
            'microsoft_calendar_token_validity':fields.Datetime.now()+timedelta(seconds=ttl)ifttlelseFalse,
        })
