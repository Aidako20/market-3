fromflectraimportapi,fields,models


classResPartner(models.Model):
    _inherit="res.partner"

    date_localization=fields.Date(string='GeolocationDate')

    @api.model
    def_geo_localize(self,street='',zip='',city='',state='',country=''):
        geo_obj=self.env['base.geocoder']
        search=geo_obj.geo_query_address(street=street,zip=zip,city=city,state=state,country=country)
        result=geo_obj.geo_find(search,force_country=country)
        ifresultisNone:
            search=geo_obj.geo_query_address(city=city,state=state,country=country)
            result=geo_obj.geo_find(search,force_country=country)
        returnresult

    defgeo_localize(self):
        #WeneedcountrynamesinEnglishbelow
        forpartnerinself.with_context(lang='en_US'):
            result=self._geo_localize(partner.street,
                                        partner.zip,
                                        partner.city,
                                        partner.state_id.name,
                                        partner.country_id.name)

            ifresult:
                partner.write({
                    'partner_latitude':result[0],
                    'partner_longitude':result[1],
                    'date_localization':fields.Date.context_today(partner)
                })
        returnTrue
