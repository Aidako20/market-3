#-*-coding:utf-8-*-

fromflectraimportexceptions,_
fromflectra.httpimportController,request,route
fromflectra.addons.bus.models.busimportdispatch


classBusController(Controller):
    """Examples:
    openerp.jsonRpc('/longpolling/poll','call',{"channels":["c1"],last:0}).then(function(r){console.log(r)});
    openerp.jsonRpc('/longpolling/send','call',{"channel":"c1","message":"m1"});
    openerp.jsonRpc('/longpolling/send','call',{"channel":"c2","message":"m2"});
    """

    @route('/longpolling/send',type="json",auth="public")
    defsend(self,channel,message):
        ifnotisinstance(channel,str):
            raiseException("bus.Busonlystringchannelsareallowed.")
        returnrequest.env['bus.bus'].sendone(channel,message)

    #overridetoaddchannels
    def_poll(self,dbname,channels,last,options):
        #updatetheuserpresence
        ifrequest.session.uidand'bus_inactivity'inoptions:
            request.env['bus.presence'].update(options.get('bus_inactivity'))
        request.cr.close()
        request._cr=None
        returndispatch.poll(dbname,channels,last,options)

    @route('/longpolling/poll',type="json",auth="public",cors="*")
    defpoll(self,channels,last,options=None):
        ifoptionsisNone:
            options={}
        ifnotdispatch:
            raiseException("bus.Busunavailable")
        if[cforcinchannelsifnotisinstance(c,str)]:
            raiseException("bus.Busonlystringchannelsareallowed.")
        ifrequest.registry.in_test_mode():
            raiseexceptions.UserError(_("bus.Busnotavailableintestmode"))
        returnself._poll(request.db,channels,last,options)

    @route('/longpolling/im_status',type="json",auth="user")
    defim_status(self,partner_ids):
        returnrequest.env['res.partner'].with_context(active_test=False).search([('id','in',partner_ids)]).read(['im_status'])
