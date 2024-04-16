#-*-coding:utf-8-*

fromflectra.addons.bus.controllers.mainimportBusController
fromflectra.httpimportrequest


classCalendarBusController(BusController):
    #--------------------------
    #ExtendsBUSControllerPoll
    #--------------------------
    def_poll(self,dbname,channels,last,options):
        ifrequest.session.uid:
            channels=list(channels)
            channels.append((request.db,'calendar.alarm',request.env.user.partner_id.id))
        returnsuper(CalendarBusController,self)._poll(dbname,channels,last,options)
