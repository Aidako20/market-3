#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportmodels,fields


classResCompany(models.Model):
    _inherit="res.company"

    def_localization_use_documents(self):
        """Chileanlocalizationusedocuments"""
        self.ensure_one()
        returnself.country_id.code=="CL"orsuper()._localization_use_documents()
