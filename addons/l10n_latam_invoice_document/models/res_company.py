#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields,models


classResCompany(models.Model):

    _inherit="res.company"

    def_localization_use_documents(self):
        """ThismethodistobeinheritedbylocalizationsandreturnTrueiflocalizationusedocuments"""
        self.ensure_one()
        returnFalse
