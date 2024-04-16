#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

#@author- FeketeMihai<feketemihai@gmail.com>
#Copyright(C)2020NextERPRomania(https://www.nexterp.ro)<contact@nexterp.ro>
#Copyright(C)2015ForestandBiomassServicesRomania(http://www.forbiom.eu).
#Copyright(C)2011TOTALPCSYSTEMS(http://www.erpsystems.ro).
#Copyright(C)2009(<http://www.filsystem.ro>)

fromflectraimportapi,fields,models


classResPartner(models.Model):
    _inherit="res.partner"

    @api.model
    def_commercial_fields(self):
        returnsuper(ResPartner,self)._commercial_fields()+['nrc']

    nrc=fields.Char(string='NRC',help='RegistrationnumberattheRegistryofCommerce')
