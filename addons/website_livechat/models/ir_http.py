#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classIrHttp(models.AbstractModel):
    _inherit='ir.http'

    @classmethod
    def_get_translation_frontend_modules_name(cls):
        mods=super(IrHttp,cls)._get_translation_frontend_modules_name()
        returnmods+['im_livechat']
