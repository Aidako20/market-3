#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime,timedelta
frompytzimporttimezone,utc

fromflectraimportapi,fields,models
fromflectra.addons.http_routing.models.ir_httpimportslug
fromflectra.addons.resource.models.resourceimportfloat_to_time
fromflectra.toolsimportis_html_empty
fromflectra.tools.translateimporthtml_translate


classEventSponsor(models.Model):
    _name='event.sponsor'
    _inherit=[
        'event.sponsor',
        'website.published.mixin',
        'chat.room.mixin',
    ]
    _rec_name='name'
    _order='sponsor_type_id,sequence'

    #description
    subtitle=fields.Char('Slogan',help='Catchymarketingsentenceforpromote')
    is_exhibitor=fields.Boolean("Exhibitor'sChat")
    website_description=fields.Html(
        'Description',compute='_compute_website_description',
        sanitize_attributes=False,sanitize_form=True,translate=html_translate,
        readonly=False,store=True)
    #livemode
    hour_from=fields.Float('Openinghour',default=8.0)
    hour_to=fields.Float('Endhour',default=18.0)
    event_date_tz=fields.Selection(string='Timezone',related='event_id.date_tz',readonly=True)
    is_in_opening_hours=fields.Boolean(
        'Withinopeninghours',compute='_compute_is_in_opening_hours')
    #chatroom
    chat_room_id=fields.Many2one(readonly=False)
    room_name=fields.Char(readonly=False)
    #countryinformation(relatedtoeasefrontendtemplates)
    country_id=fields.Many2one(
        'res.country',string='Country',
        related='partner_id.country_id',readonly=True)
    country_flag_url=fields.Char(
        string='CountryFlag',
        compute='_compute_country_flag_url',compute_sudo=True)

    @api.onchange('is_exhibitor')
    def_onchange_is_exhibitor(self):
        """Keepanexplicitonchangetoallowconfigurationofroomnames,even
        ifthisfieldisnormallyarelatedonchat_room_id.name.Itisnotareal
        computedfield,anonchangeusedinformviewissufficient."""
        forsponsorinself:
            ifsponsor.is_exhibitorandnotsponsor.room_name:
                ifsponsor.name:
                    room_name="flectra-exhibitor-%s"%sponsor.name
                else:
                    room_name=self.env['chat.room']._default_name(objname='exhibitor')
                sponsor.room_name=self._jitsi_sanitize_name(room_name)
            ifsponsor.is_exhibitorandnotsponsor.room_max_capacity:
                sponsor.room_max_capacity='8'

    @api.depends('partner_id')
    def_compute_website_description(self):
        forsponsorinself:
            ifis_html_empty(sponsor.website_description):
                sponsor.website_description=sponsor.partner_id.website_description

    @api.depends('event_id.is_ongoing','hour_from','hour_to','event_id.date_begin','event_id.date_end')
    def_compute_is_in_opening_hours(self):
        """Openinghours:hour_fromandhour_toaregivenwithineventTZorUTC.
        Now()mustthereforebecomputedbasedonthatTZ."""
        forsponsorinself:
            ifnotsponsor.event_id.is_ongoing:
                sponsor.is_in_opening_hours=False
            elifsponsor.hour_fromisFalseorsponsor.hour_toisFalse:
                sponsor.is_in_opening_hours=True
            else:
                event_tz=timezone(sponsor.event_id.date_tz)
                #localizenow,beginandenddatetimesineventtz
                dt_begin=sponsor.event_id.date_begin.astimezone(event_tz)
                dt_end=sponsor.event_id.date_end.astimezone(event_tz)
                now_utc=utc.localize(fields.Datetime.now().replace(microsecond=0))
                now_tz=now_utc.astimezone(event_tz)

                #computeopeninghours
                opening_from_tz=event_tz.localize(datetime.combine(now_tz.date(),float_to_time(sponsor.hour_from)))
                opening_to_tz=event_tz.localize(datetime.combine(now_tz.date(),float_to_time(sponsor.hour_to)))
                ifsponsor.hour_to==0:
                    #whenclosing'atmidnight',weconsiderit'satmidnightthenextday
                    opening_to_tz=opening_to_tz+timedelta(days=1)

                opening_from=max([dt_begin,opening_from_tz])
                opening_to=min([dt_end,opening_to_tz])

                sponsor.is_in_opening_hours=opening_from<=now_tz<opening_to

    @api.depends('partner_id.country_id.image_url')
    def_compute_country_flag_url(self):
        forsponsorinself:
            ifsponsor.partner_id.country_id:
                sponsor.country_flag_url=sponsor.partner_id.country_id.image_url
            else:
                sponsor.country_flag_url=False

    #------------------------------------------------------------
    #MIXINS
    #---------------------------------------------------------

    @api.depends('name','event_id.name')
    def_compute_website_url(self):
        super(EventSponsor,self)._compute_website_url()
        forsponsorinself:
            ifsponsor.id: #avoidtoperformaslugonanotyetsavedrecordincaseofanonchange.
                base_url=sponsor.event_id.get_base_url()
                sponsor.website_url='%s/event/%s/exhibitor/%s'%(base_url,slug(sponsor.event_id),slug(sponsor))

    #------------------------------------------------------------
    #CRUD
    #------------------------------------------------------------

    @api.model_create_multi
    defcreate(self,values_list):
        forvaluesinvalues_list:
            ifvalues.get('is_exhibitor')andnotvalues.get('room_name'):
                exhibitor_name=values['name']ifvalues.get('name')elseself.env['res.partner'].browse(values['partner_id']).name
                name='flectra-exhibitor-%s'%exhibitor_nameor'sponsor'
                values['room_name']=name
        returnsuper(EventSponsor,self).create(values_list)

    defwrite(self,values):
        toupdate=self.env['event.sponsor']
        ifvalues.get('is_exhibitor')andnotvalues.get('chat_room_id')andnotvalues.get('room_name'):
            toupdate=self.filtered(lambdaexhibitor:notexhibitor.chat_room_id)
            #gointosequentialupdateinordertocreateacustomroomnameforeachsponsor
            forexhibitorintoupdate:
                values['room_name']='flectra-exhibitor-%s'%exhibitor.name
                super(EventSponsor,exhibitor).write(values)
        returnsuper(EventSponsor,self-toupdate).write(values)

    #------------------------------------------------------------
    #ACTIONS
    #---------------------------------------------------------

    defget_backend_menu_id(self):
        returnself.env.ref('event.event_main_menu').id
