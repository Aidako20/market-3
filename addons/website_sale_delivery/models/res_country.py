#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResCountry(models.Model):
    _inherit='res.country'

    defget_website_sale_countries(self,mode='billing'):
        res=super(ResCountry,self).get_website_sale_countries(mode=mode)
        ifmode=='shipping':
            countries=self.env['res.country']

            delivery_carriers=self.env['delivery.carrier'].sudo().search([('website_published','=',True)])
            forcarrierindelivery_carriers:
                ifnotcarrier.country_idsandnotcarrier.state_ids:
                    countries=res
                    break
                countries|=carrier.country_ids

            res=res&countries
        returnres

    defget_website_sale_states(self,mode='billing'):
        res=super(ResCountry,self).get_website_sale_states(mode=mode)

        states=self.env['res.country.state']
        ifmode=='shipping':
            dom=['|',('country_ids','in',self.id),('country_ids','=',False),('website_published','=',True)]
            delivery_carriers=self.env['delivery.carrier'].sudo().search(dom)

            forcarrierindelivery_carriers:
                ifnotcarrier.country_idsornotcarrier.state_ids:
                    states=res
                    break
                states|=carrier.state_ids
            res=res&states
        returnres
