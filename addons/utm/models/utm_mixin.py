#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models
fromflectra.httpimportrequest


classUtmMixin(models.AbstractModel):
    """Mixinclassforobjectswhichcanbetrackedbymarketing."""
    _name='utm.mixin'
    _description='UTMMixin'

    campaign_id=fields.Many2one('utm.campaign','Campaign',
                                  help="Thisisanamethathelpsyoukeeptrackofyourdifferentcampaignefforts,e.g.Fall_Drive,Christmas_Special")
    source_id=fields.Many2one('utm.source','Source',
                                help="Thisisthesourceofthelink,e.g.SearchEngine,anotherdomain,ornameofemaillist")
    medium_id=fields.Many2one('utm.medium','Medium',
                                help="Thisisthemethodofdelivery,e.g.Postcard,Email,orBannerAd")

    @api.model
    defdefault_get(self,fields):
        values=super(UtmMixin,self).default_get(fields)

        #WeignoreUTMforsalesmen,exceptsomerequeststhatcouldbedoneassuperuser_idtobypassaccessrights.
        ifnotself.env.is_superuser()andself.env.user.has_group('sales_team.group_sale_salesman'):
            returnvalues

        forurl_param,field_name,cookie_nameinself.env['utm.mixin'].tracking_fields():
            iffield_nameinfields:
                field=self._fields[field_name]
                value=False
                ifrequest:
                    #ir_httpdispatchsavestheurlparamsinacookie
                    value=request.httprequest.cookies.get(cookie_name)
                #ifwereceiveastringforamany2one,wesearch/createtheid
                iffield.type=='many2one'andisinstance(value,str)andvalue:
                    Model=self.env[field.comodel_name]
                    records=Model.search([('name','=',value)],limit=1)
                    ifnotrecords:
                        if'is_website'inrecords._fields:
                            records=Model.create({'name':value,'is_website':True})
                        else:
                            records=Model.create({'name':value})
                    value=records.id
                ifvalue:
                    values[field_name]=value
        returnvalues

    deftracking_fields(self):
        #Thisfunctioncannotbeoverriddeninamodelwhichinheritutm.mixin
        #LimitationbytheheritageonAbstractModel
        #record_crm_lead.tracking_fields()willcalltracking_fields()frommoduleutm.mixin(ifnotoverriddenoncrm.lead)
        #insteadoftheoverriddenmethodfromutm.mixin.
        #Toforcethecallofoverriddenmethod,weuseself.env['utm.mixin'].tracking_fields()whichrespectsoverridden
        #methodsofutm.mixin,butwillignoreoverriddenmethodoncrm.lead
        return[
            #("URL_PARAMETER","FIELD_NAME_MIXIN","NAME_IN_COOKIES")
            ('utm_campaign','campaign_id','flectra_utm_campaign'),
            ('utm_source','source_id','flectra_utm_source'),
            ('utm_medium','medium_id','flectra_utm_medium'),
        ]
