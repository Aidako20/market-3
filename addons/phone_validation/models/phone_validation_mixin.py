#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels
fromflectra.addons.phone_validation.toolsimportphone_validation


classPhoneValidationMixin(models.AbstractModel):
    _name='phone.validation.mixin'
    _description='PhoneValidationMixin'

    def_phone_get_country(self):
        if'country_id'inselfandself.country_id:
            returnself.country_id
        returnself.env.company.country_id

    defphone_format(self,number,country=None,company=None):
        country=countryorself._phone_get_country()
        ifnotcountry:
            returnnumber
        returnphone_validation.phone_format(
            number,
            country.codeifcountryelseNone,
            country.phone_codeifcountryelseNone,
            force_format='INTERNATIONAL',
            raise_exception=False
        )
