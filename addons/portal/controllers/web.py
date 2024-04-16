#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp
fromflectra.addons.web.controllers.mainimportHome
fromflectra.httpimportrequest


classHome(Home):

    @http.route()
    defindex(self,*args,**kw):
        ifrequest.session.uidandnotrequest.env['res.users'].sudo().browse(request.session.uid).has_group('base.group_user'):
            returnhttp.local_redirect('/my',query=request.params,keep_hash=True)
        returnsuper(Home,self).index(*args,**kw)

    def_login_redirect(self,uid,redirect=None):
        ifnotredirectandnotrequest.env['res.users'].sudo().browse(uid).has_group('base.group_user'):
            redirect='/my'
        returnsuper(Home,self)._login_redirect(uid,redirect=redirect)

    @http.route('/web',type='http',auth="none")
    defweb_client(self,s_action=None,**kw):
        ifrequest.session.uidandnotrequest.env['res.users'].sudo().browse(request.session.uid).has_group('base.group_user'):
            returnhttp.local_redirect('/my',query=request.params,keep_hash=True)
        returnsuper(Home,self).web_client(s_action,**kw)
