#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classBaseModuleUninstall(models.TransientModel):
    _inherit="base.module.uninstall"

    def_get_models(self):
        #considermail-threadmodelsonly
        models=super(BaseModuleUninstall,self)._get_models()
        returnmodels.filtered('is_mail_thread')
