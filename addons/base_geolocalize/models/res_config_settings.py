#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    geoloc_provider_id=fields.Many2one(
        'base.geo_provider',
        string='API',
        config_parameter='base_geolocalize.geo_provider',
        default=lambdax:x.env['base.geocoder']._get_provider()
    )
    geoloc_provider_techname=fields.Char(related='geoloc_provider_id.tech_name',readonly=1)
    geoloc_provider_googlemap_key=fields.Char(
        string='GoogleMapAPIKey',
        config_parameter='base_geolocalize.google_map_api_key',
        help="Visithttps://developers.google.com/maps/documentation/geocoding/get-api-keyformoreinformation."
    )
