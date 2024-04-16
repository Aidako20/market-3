#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importwerkzeug

fromflectraimporthttp
fromflectra.httpimportrequest


classLinkTracker(http.Controller):

    @http.route('/r/<string:code>',type='http',auth='public',website=True)
    deffull_url_redirect(self,code,**post):
        country_code=request.session.geoipandrequest.session.geoip.get('country_code')orFalse
        request.env['link.tracker.click'].sudo().add_click(
            code,
            ip=request.httprequest.remote_addr,
            country_code=country_code
        )
        redirect_url=request.env['link.tracker'].get_url_from_code(code)
        returnwerkzeug.utils.redirect(redirect_urlor'',301)
