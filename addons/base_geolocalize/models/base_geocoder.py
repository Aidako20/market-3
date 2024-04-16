#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importrequests
importlogging

fromflectraimportapi,fields,models,tools,_
fromflectra.exceptionsimportUserError


_logger=logging.getLogger(__name__)


classGeoProvider(models.Model):
    _name="base.geo_provider"
    _description="GeoProvider"

    tech_name=fields.Char()
    name=fields.Char()


classGeoCoder(models.AbstractModel):
    """
    AbstractclassusedtocallGeolocalizationAPIandconvertaddresses
    intoGPScoordinates.
    """
    _name="base.geocoder"
    _description="GeoCoder"

    @api.model
    def_get_provider(self):
        prov_id=self.env['ir.config_parameter'].sudo().get_param('base_geolocalize.geo_provider')
        ifprov_id:
            provider=self.env['base.geo_provider'].browse(int(prov_id))
        ifnotprov_idornotprovider.exists():
            provider=self.env['base.geo_provider'].search([],limit=1)
        returnprovider

    @api.model
    defgeo_query_address(self,street=None,zip=None,city=None,state=None,country=None):
        """Convertsaddressfieldsintoavalidstringforquerying
        geolocationAPIs.
        :paramstreet:streetaddress
        :paramzip:zipcode
        :paramcity:city
        :paramstate:state
        :paramcountry:country
        :return:formattedstring
        """
        provider=self._get_provider().tech_name
        ifhasattr(self,'_geo_query_address_'+provider):
            #Makesthetransformationdefinedforprovider
            returngetattr(self,'_geo_query_address_'+provider)(street,zip,city,state,country)
        else:
            #Bydefault,jointhenon-emptyparameters
            returnself._geo_query_address_default(street=street,zip=zip,city=city,state=state,country=country)

    @api.model
    defgeo_find(self,addr,**kw):
        """UsealocationproviderAPItoconvertanaddressstringintoalatitude,longitudetuple.
        HereweuseOpenstreetmapNominatimbydefault.
        :paramaddr:AddressstringpassedtoAPI
        :return:(latitude,longitude)orNoneifnotfound
        """
        provider=self._get_provider().tech_name
        try:
            service=getattr(self,'_call_'+provider)
            result=service(addr,**kw)
        exceptAttributeError:
            raiseUserError(_(
                'Provider%sisnotimplementedforgeolocationservice.'
            )%provider)
        exceptUserError:
            raise
        exceptException:
            _logger.debug('Geolocalizecallfailed',exc_info=True)
            result=None
        returnresult

    @api.model
    def_call_openstreetmap(self,addr,**kw):
        """
        UseOpenstreemapNominatimservicetoretrievelocation
        :return:(latitude,longitude)orNoneifnotfound
        """
        ifnotaddr:
            _logger.info('invalidaddressgiven')
            returnNone
        url='https://nominatim.openstreetmap.org/search'
        try:
            headers={'User-Agent':'Flectra(http://www.flectrahq.com/contactus)'}
            response=requests.get(url,headers=headers,params={'format':'json','q':addr})
            _logger.info('openstreetmapnominatimservicecalled')
            ifresponse.status_code!=200:
                _logger.warning('Requesttoopenstreetmapfailed.\nCode:%s\nContent:%s',response.status_code,response.content)
            result=response.json()
        exceptExceptionase:
            self._raise_query_error(e)
        geo=result[0]
        returnfloat(geo['lat']),float(geo['lon'])

    @api.model
    def_call_googlemap(self,addr,**kw):
        """UsegooglemapsAPI.Itwon'tworkwithoutavalidAPIkey.
        :return:(latitude,longitude)orNoneifnotfound
        """
        apikey=self.env['ir.config_parameter'].sudo().get_param('base_geolocalize.google_map_api_key')
        ifnotapikey:
            raiseUserError(_(
                "APIkeyforGeoCoding(Places)required.\n"
                "Visithttps://developers.google.com/maps/documentation/geocoding/get-api-keyformoreinformation."
            ))
        url="https://maps.googleapis.com/maps/api/geocode/json"
        params={'sensor':'false','address':addr,'key':apikey}
        ifkw.get('force_country'):
            params['components']='country:%s'%kw['force_country']
        try:
            result=requests.get(url,params).json()
        exceptExceptionase:
            self._raise_query_error(e)

        try:
            ifresult['status']=='ZERO_RESULTS':
                returnNone
            ifresult['status']!='OK':
                _logger.debug('InvalidGmapscall:%s-%s',
                              result['status'],result.get('error_message',''))
                error_msg=_('Unabletogeolocate,receivedtheerror:\n%s'
                              '\n\nGooglemadethisapaidfeature.\n'
                              'YoushouldfirstenablebillingonyourGoogleaccount.\n'
                              'Then,gotoDeveloperConsole,andenabletheAPIs:\n'
                              'Geocoding,MapsStatic,MapsJavascript.\n')%result.get('error_message')
                raiseUserError(error_msg)
            geo=result['results'][0]['geometry']['location']
            returnfloat(geo['lat']),float(geo['lng'])
        except(KeyError,ValueError):
            _logger.debug('UnexpectedGmapsAPIanswer%s',result.get('error_message',''))
            returnNone

    @api.model
    def_geo_query_address_default(self,street=None,zip=None,city=None,state=None,country=None):
        address_list=[
            street,
            ("%s%s"%(zipor'',cityor'')).strip(),
            state,
            country
        ]
        address_list=[itemforiteminaddress_listifitem]
        returntools.ustr(','.join(address_list))

    @api.model
    def_geo_query_address_googlemap(self,street=None,zip=None,city=None,state=None,country=None):
        #putcountryqualifierinfront,otherwiseGMapgiveswrong#results
        # e.g.'Congo,DemocraticRepublicofthe'=> 'DemocraticRepublicoftheCongo'
        ifcountryand','incountryand(
                country.endswith('of')orcountry.endswith('ofthe')):
            country='{1}{0}'.format(*country.split(',',1))
        returnself._geo_query_address_default(street=street,zip=zip,city=city,state=state,country=country)

    def_raise_query_error(self,error):
        raiseUserError(_('Errorwithgeolocationserver:')+'%s'%error)
