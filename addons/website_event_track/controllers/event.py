#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.website_event.controllers.mainimportWebsiteEventController


classEventOnlineController(WebsiteEventController):

    def_get_registration_confirm_values(self,event,attendees_sudo):
        values=super(EventOnlineController,self)._get_registration_confirm_values(event,attendees_sudo)
        values['hide_sponsors']=True
        returnvalues
