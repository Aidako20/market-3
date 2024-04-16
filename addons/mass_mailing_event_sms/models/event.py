#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classEvent(models.Model):
    _inherit="event.event"

    defaction_mass_mailing_attendees(self):
        #Minimaloverride:setformviewbeingtheonemixingsmsandmail(notprioritizedone)
        action=super(Event,self).action_mass_mailing_attendees()
        action['view_id']=self.env.ref('mass_mailing_sms.mailing_mailing_view_form_mixed').id
        returnaction

    defaction_invite_contacts(self):
        #Minimaloverride:setformviewbeingtheonemixingsmsandmail(notprioritizedone)
        action=super(Event,self).action_invite_contacts()
        action['view_id']=self.env.ref('mass_mailing_sms.mailing_mailing_view_form_mixed').id
        returnaction
