#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels
fromflectra.httpimportrequest


classIrHttp(models.AbstractModel):
    _inherit='ir.http'

    @classmethod
    def_get_translation_frontend_modules_name(cls):
        mods=super(IrHttp,cls)._get_translation_frontend_modules_name()
        returnmods+['portal']

    @classmethod
    def_get_frontend_langs(cls):
        ifrequestandrequest.is_frontend:
            return[lang[0]forlanginfilter(lambdal:l[3],request.env['res.lang'].get_available())]
        returnsuper()._get_frontend_langs()
