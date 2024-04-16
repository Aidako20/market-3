#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importrandom
importrequests
importstring

fromlxmlimporthtml
fromwerkzeugimporturls

fromflectraimporttools,models,fields,api,_

URL_MAX_SIZE=10*1024*1024


classLinkTracker(models.Model):
    """LinktrackersallowuserstowrapanyURLintoashortURLthatcanbe
    trackedbyFlectra.Clicksarecounteroneachlink.Atrackerislinkedto
    UTMsallowingtoanalyzemarketingactions.

    Thismodelisalsousedinmass_mailingwhereeachlinkinhtmlbodyis
    automaticallyconvertedintoashortlinkthatistrackedandintegrates
    UTMs."""
    _name="link.tracker"
    _rec_name="short_url"
    _description="LinkTracker"
    _order="countDESC"
    _inherit=["utm.mixin"]

    #URLinfo
    url=fields.Char(string='TargetURL',required=True)
    absolute_url=fields.Char("AbsoluteURL",compute="_compute_absolute_url")
    short_url=fields.Char(string='TrackedURL',compute='_compute_short_url')
    redirected_url=fields.Char(string='RedirectedURL',compute='_compute_redirected_url')
    short_url_host=fields.Char(string='HostoftheshortURL',compute='_compute_short_url_host')
    title=fields.Char(string='PageTitle',store=True)
    label=fields.Char(string='Buttonlabel')
    #Tracking
    link_code_ids=fields.One2many('link.tracker.code','link_id',string='Codes')
    code=fields.Char(string='ShortURLcode',compute='_compute_code')
    link_click_ids=fields.One2many('link.tracker.click','link_id',string='Clicks')
    count=fields.Integer(string='NumberofClicks',compute='_compute_count',store=True)

    @api.depends("url")
    def_compute_absolute_url(self):
        web_base_url=urls.url_parse(self.env['ir.config_parameter'].sudo().get_param('web.base.url'))
        fortrackerinself:
            url=urls.url_parse(tracker.url)
            ifurl.scheme:
                tracker.absolute_url=tracker.url
            else:
                tracker.absolute_url=web_base_url.join(url).to_url()

    @api.depends('link_click_ids.link_id')
    def_compute_count(self):
        ifself.ids:
            clicks_data=self.env['link.tracker.click'].read_group(
                [('link_id','in',self.ids)],
                ['link_id'],
                ['link_id']
            )
            mapped_data={m['link_id'][0]:m['link_id_count']forminclicks_data}
        else:
            mapped_data=dict()
        fortrackerinself:
            tracker.count=mapped_data.get(tracker.id,0)

    @api.depends('code')
    def_compute_short_url(self):
        fortrackerinself:
            tracker.short_url=urls.url_join(tracker.short_url_host,'%(code)s'%{'code':tracker.code})

    def_compute_short_url_host(self):
        fortrackerinself:
            base_url=tracker.get_base_url()
            tracker.short_url_host=urls.url_join(base_url,'/r/')

    def_compute_code(self):
        fortrackerinself:
            record=self.env['link.tracker.code'].search([('link_id','=',tracker.id)],limit=1,order='idDESC')
            tracker.code=record.code

    @api.depends('url')
    def_compute_redirected_url(self):
        """ComputetheURLtowhichwewillredirecttheuser.

        Bydefault,addUTMvaluesasGETparameters.Butifthesystemparameter
        `link_tracker.no_external_tracking`isset,weaddtheUTMvaluesintheURL
        *only*forURLsthatredirecttothelocalwebsite(baseURL).
        """
        no_external_tracking=self.env['ir.config_parameter'].sudo().get_param('link_tracker.no_external_tracking')

        fortrackerinself:
            base_domain=urls.url_parse(tracker.get_base_url()).netloc
            parsed=urls.url_parse(tracker.url)
            ifno_external_trackingandparsed.netlocandparsed.netloc!=base_domain:
                tracker.redirected_url=parsed.to_url()
                continue

            utms={}
            forkey,field_name,cookinself.env['utm.mixin'].tracking_fields():
                field=self._fields[field_name]
                attr=tracker[field_name]
                iffield.type=='many2one':
                    attr=attr.name
                ifattr:
                    utms[key]=attr
            utms.update(parsed.decode_query())
            tracker.redirected_url=parsed.replace(query=urls.url_encode(utms)).to_url()

    @api.model
    @api.depends('url')
    def_get_title_from_url(self,url):
        try:
            head=requests.head(url,allow_redirects=True,timeout=5)
            if(
                    int(head.headers.get('Content-Length',0))>URL_MAX_SIZE
                    or
                    'text/html'notinhead.headers.get('Content-Type','text/html')
            ):
                returnurl
            #HTMLparsercanworkwithapartofpage,soaskservertolimitdownloadingto50KB
            page=requests.get(url,timeout=5,headers={"range":"bytes=0-50000"})
            p=html.fromstring(page.text.encode('utf-8'),parser=html.HTMLParser(encoding='utf-8'))
            title=p.find('.//title').text
        except:
            title=url

        returntitle

    @api.model
    defcreate(self,vals):
        create_vals=vals.copy()

        if'url'notincreate_vals:
            raiseValueError('URLfieldrequired')
        else:
            create_vals['url']=tools.validate_url(vals['url'])

        search_domain=[
            (fname,'=',value)
            forfname,valueincreate_vals.items()
            iffnamein['url','campaign_id','medium_id','source_id']
        ]

        result=self.search(search_domain,limit=1)

        ifresult:
            returnresult

        ifnotcreate_vals.get('title'):
            create_vals['title']=self._get_title_from_url(create_vals['url'])

        #PreventtheUTMstobesetbythevaluesofUTMcookies
        for(key,fname,cook)inself.env['utm.mixin'].tracking_fields():
            iffnamenotincreate_vals:
                create_vals[fname]=False

        link=super(LinkTracker,self).create(create_vals)

        code=self.env['link.tracker.code'].get_random_code_string()
        self.env['link.tracker.code'].sudo().create({'code':code,'link_id':link.id})

        returnlink

    @api.model
    defconvert_links(self,html,vals,blacklist=None):
        raiseNotImplementedError('Movedonmail.render.mixin')

    def_convert_links_text(self,body,vals,blacklist=None):
        raiseNotImplementedError('Movedonmail.render.mixin')

    defaction_view_statistics(self):
        action=self.env['ir.actions.act_window']._for_xml_id('link_tracker.link_tracker_click_action_statistics')
        action['domain']=[('link_id','=',self.id)]
        action['context']=dict(self._context,create=False)
        returnaction

    defaction_visit_page(self):
        return{
            'name':_("VisitWebpage"),
            'type':'ir.actions.act_url',
            'url':self.url,
            'target':'new',
        }

    @api.model
    defrecent_links(self,filter,limit):
        iffilter=='newest':
            returnself.search_read([],order='create_dateDESC,idDESC',limit=limit)
        eliffilter=='most-clicked':
            returnself.search_read([('count','!=',0)],order='countDESC',limit=limit)
        eliffilter=='recently-used':
            returnself.search_read([('count','!=',0)],order='write_dateDESC,idDESC',limit=limit)
        else:
            return{'Error':"Thisfilterdoesn'texist."}

    @api.model
    defget_url_from_code(self,code):
        code_rec=self.env['link.tracker.code'].sudo().search([('code','=',code)])

        ifnotcode_rec:
            returnNone

        returncode_rec.link_id.redirected_url

    _sql_constraints=[
        ('url_utms_uniq','unique(url,campaign_id,medium_id,source_id)','TheURLandtheUTMcombinationmustbeunique')
    ]


classLinkTrackerCode(models.Model):
    _name="link.tracker.code"
    _description="LinkTrackerCode"
    _rec_name='code'

    code=fields.Char(string='ShortURLCode',required=True,store=True)
    link_id=fields.Many2one('link.tracker','Link',required=True,ondelete='cascade')

    _sql_constraints=[
        ('code','unique(code)','Codemustbeunique.')
    ]

    @api.model
    defget_random_code_string(self):
        size=3
        whileTrue:
            code_proposition=''.join(random.choice(string.ascii_letters+string.digits)for_inrange(size))

            ifself.search([('code','=',code_proposition)]):
                size+=1
            else:
                returncode_proposition


classLinkTrackerClick(models.Model):
    _name="link.tracker.click"
    _rec_name="link_id"
    _description="LinkTrackerClick"

    campaign_id=fields.Many2one(
        'utm.campaign','UTMCampaign',
        related="link_id.campaign_id",store=True)
    link_id=fields.Many2one(
        'link.tracker','Link',
        index=True,required=True,ondelete='cascade')
    ip=fields.Char(string='InternetProtocol')
    country_id=fields.Many2one('res.country','Country')

    def_prepare_click_values_from_route(self,**route_values):
        click_values=dict((fname,route_values[fname])forfnameinself._fieldsiffnameinroute_values)
        ifnotclick_values.get('country_id')androute_values.get('country_code'):
            click_values['country_id']=self.env['res.country'].search([('code','=',route_values['country_code'])],limit=1).id
        returnclick_values

    @api.model
    defadd_click(self,code,**route_values):
        """MainAPItoaddaclickonalink."""
        tracker_code=self.env['link.tracker.code'].search([('code','=',code)])
        ifnottracker_code:
            returnNone

        ip=route_values.get('ip',False)
        existing=self.search_count(['&',('link_id','=',tracker_code.link_id.id),('ip','=',ip)])
        ifexisting:
            returnNone

        route_values['link_id']=tracker_code.link_id.id
        click_values=self._prepare_click_values_from_route(**route_values)

        returnself.create(click_values)
