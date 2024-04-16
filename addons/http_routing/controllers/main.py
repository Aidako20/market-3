#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp
fromflectra.httpimportrequest
fromflectra.addons.web.controllers.mainimportWebClient,Home


classRouting(Home):

    @http.route('/website/translations/<string:unique>',type='http',auth="public",website=True)
    defget_website_translations(self,unique,lang,mods=None):
        IrHttp=request.env['ir.http'].sudo()
        modules=IrHttp.get_translation_frontend_modules()
        ifmods:
            modules+=mods.split(',')ifisinstance(mods,str)elsemods
        returnWebClient().translations(unique,mods=','.join(modules),lang=lang)
