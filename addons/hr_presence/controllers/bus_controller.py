#-*-coding:utf-8-*-

fromflectraimportregistry,SUPERUSER_ID
fromflectra.apiimportEnvironment
fromflectra.addons.bus.controllers.mainimportBusController
fromflectra.fieldsimportDatetime
fromflectra.httpimportController,request,route


classBusController(BusController):

    @route('/longpolling/poll',type="json",auth="public")
    defpoll(self,channels,last,options=None):
        ifrequest.env.user.has_group('base.group_user'):
            ip_address=request.httprequest.remote_addr
            users_log=request.env['res.users.log'].search_count([
                ('create_uid','=',request.env.user.id),
                ('ip','=',ip_address),
                ('create_date','>=',Datetime.to_string(Datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)))])
            ifnotusers_log:
                withregistry(request.env.cr.dbname).cursor()ascr:
                    env=Environment(cr,request.env.user.id,{})
                    env['res.users.log'].create({'ip':ip_address})
        returnsuper(BusController,self).poll(channels,last,options=options)
