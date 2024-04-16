#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportmodels
fromflectra.exceptionsimportUserError
fromflectra.tools.translateimport_


classpos_config(models.Model):
    _inherit='pos.config'

    defopen_ui(self):
        forconfiginself:
            ifnotconfig.company_id.country_id:
                raiseUserError(_("Youhavetosetacountryinyourcompanysetting."))
        returnsuper(pos_config,self).open_ui()
