#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,fields
fromflectra.httpimportrequest
fromflectra.addons.http_routing.models.ir_httpimporturl_for


classView(models.Model):
    _inherit="ir.ui.view"

    customize_show=fields.Boolean("ShowAsOptionalInherit",default=False)

    @api.model
    def_prepare_qcontext(self):
        """Returnstheqcontext:renderingcontextwithportalspecificvalue(required
            torenderportallayouttemplate)
        """
        qcontext=super(View,self)._prepare_qcontext()
        ifrequestandgetattr(request,'is_frontend',False):
            Lang=request.env['res.lang']
            portal_lang_code=request.env['ir.http']._get_frontend_langs()
            qcontext.update(dict(
                self._context.copy(),
                languages=[langforlanginLang.get_available()iflang[0]inportal_lang_code],
                url_for=url_for,
            ))
        returnqcontext
