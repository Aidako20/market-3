#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels
fromflectra.httpimportrequest


classIrHttp(models.AbstractModel):
    _inherit='ir.http'

    @classmethod
    def_dispatch(cls):
        context=dict(request.context)
        if'editable'inrequest.httprequest.argsand'editable'notincontext:
            context['editable']=True
        if'edit_translations'inrequest.httprequest.argsand'edit_translations'notincontext:
            context['edit_translations']=True
        ifcontext.get('edit_translations')and'translatable'notincontext:
            context['translatable']=True
        request.context=context
        returnsuper(IrHttp,cls)._dispatch()

    @classmethod
    def_get_translation_frontend_modules_name(cls):
        mods=super(IrHttp,cls)._get_translation_frontend_modules_name()
        returnmods+['web_editor']
