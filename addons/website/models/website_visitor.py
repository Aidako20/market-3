#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime,timedelta
importuuid
importpytz

fromflectraimportfields,models,api,_
fromflectra.addons.base.models.res_partnerimport_tz_get
fromflectra.exceptionsimportUserError
fromflectra.tools.miscimport_format_time_ago
fromflectra.httpimportrequest
fromflectra.osvimportexpression


classWebsiteTrack(models.Model):
    _name='website.track'
    _description='VisitedPages'
    _order='visit_datetimeDESC'
    _log_access=False

    visitor_id=fields.Many2one('website.visitor',ondelete="cascade",index=True,required=True,readonly=True)
    page_id=fields.Many2one('website.page',index=True,ondelete='cascade',readonly=True)
    url=fields.Text('Url',index=True)
    visit_datetime=fields.Datetime('VisitDate',default=fields.Datetime.now,required=True,readonly=True)


classWebsiteVisitor(models.Model):
    _name='website.visitor'
    _description='WebsiteVisitor'
    _order='last_connection_datetimeDESC'

    name=fields.Char('Name')
    access_token=fields.Char(required=True,default=lambdax:uuid.uuid4().hex,index=False,copy=False,groups='base.group_website_publisher')
    active=fields.Boolean('Active',default=True)
    website_id=fields.Many2one('website',"Website",readonly=True)
    partner_id=fields.Many2one('res.partner',string="LinkedPartner",help="Partnerofthelastloggedinuser.")
    partner_image=fields.Binary(related='partner_id.image_1920')

    #localisationandinfo
    country_id=fields.Many2one('res.country','Country',readonly=True)
    country_flag=fields.Char(related="country_id.image_url",string="CountryFlag")
    lang_id=fields.Many2one('res.lang',string='Language',help="Languagefromthewebsitewhenvisitorhasbeencreated")
    timezone=fields.Selection(_tz_get,string='Timezone')
    email=fields.Char(string='Email',compute='_compute_email_phone',compute_sudo=True)
    mobile=fields.Char(string='MobilePhone',compute='_compute_email_phone',compute_sudo=True)

    #Visitfields
    visit_count=fields.Integer('Numberofvisits',default=1,readonly=True,help="Anewvisitisconsiderediflastconnectionwasmorethan8hoursago.")
    website_track_ids=fields.One2many('website.track','visitor_id',string='VisitedPagesHistory',readonly=True)
    visitor_page_count=fields.Integer('PageViews',compute="_compute_page_statistics",help="Totalnumberofvisitsontrackedpages")
    page_ids=fields.Many2many('website.page',string="VisitedPages",compute="_compute_page_statistics",groups="website.group_website_designer",search="_search_page_ids")
    page_count=fields.Integer('#VisitedPages',compute="_compute_page_statistics",help="Totalnumberoftrackedpagevisited")
    last_visited_page_id=fields.Many2one('website.page',string="LastVisitedPage",compute="_compute_last_visited_page_id")

    #Timefields
    create_date=fields.Datetime('Firstconnectiondate',readonly=True)
    last_connection_datetime=fields.Datetime('LastConnection',default=fields.Datetime.now,help="Lastpageviewdate",readonly=True)
    time_since_last_action=fields.Char('Lastaction',compute="_compute_time_statistics",help='Timesincelastpageview.E.g.:2minutesago')
    is_connected=fields.Boolean('Isconnected?',compute='_compute_time_statistics',help='Avisitorisconsideredasconnectedifhislastpageviewwaswithinthelast5minutes.')

    _sql_constraints=[
        ('access_token_unique','unique(access_token)','Accesstokenshouldbeunique.'),
        ('partner_uniq','unique(partner_id)','Apartnerislinkedtoonlyonevisitor.'),
    ]

    @api.depends('name')
    defname_get(self):
        res=[]
        forrecordinself:
            res.append((
                record.id,
                record.nameor_('WebsiteVisitor#%s',record.id)
            ))
        returnres

    @api.depends('partner_id.email_normalized','partner_id.mobile','partner_id.phone')
    def_compute_email_phone(self):
        results=self.env['res.partner'].search_read(
            [('id','in',self.partner_id.ids)],
            ['id','email_normalized','mobile','phone'],
        )
        mapped_data={
            result['id']:{
                'email_normalized':result['email_normalized'],
                'mobile':result['mobile']ifresult['mobile']elseresult['phone']
            }forresultinresults
        }

        forvisitorinself:
            visitor.email=mapped_data.get(visitor.partner_id.id,{}).get('email_normalized')
            visitor.mobile=mapped_data.get(visitor.partner_id.id,{}).get('mobile')

    @api.depends('website_track_ids')
    def_compute_page_statistics(self):
        results=self.env['website.track'].read_group(
            [('visitor_id','in',self.ids),('url','!=',False)],['visitor_id','page_id','url'],['visitor_id','page_id','url'],lazy=False)
        mapped_data={}
        forresultinresults:
            visitor_info=mapped_data.get(result['visitor_id'][0],{'page_count':0,'visitor_page_count':0,'page_ids':set()})
            visitor_info['visitor_page_count']+=result['__count']
            visitor_info['page_count']+=1
            ifresult['page_id']:
                visitor_info['page_ids'].add(result['page_id'][0])
            mapped_data[result['visitor_id'][0]]=visitor_info

        forvisitorinself:
            visitor_info=mapped_data.get(visitor.id,{'page_count':0,'visitor_page_count':0,'page_ids':set()})
            visitor.page_ids=[(6,0,visitor_info['page_ids'])]
            visitor.visitor_page_count=visitor_info['visitor_page_count']
            visitor.page_count=visitor_info['page_count']

    def_search_page_ids(self,operator,value):
        ifoperatornotin('like','ilike','notlike','notilike','=like','=ilike','=','!='):
            raiseValueError(_('Thisoperatorisnotsupported'))
        return[('website_track_ids.page_id.name',operator,value)]

    @api.depends('website_track_ids.page_id')
    def_compute_last_visited_page_id(self):
        results=self.env['website.track'].read_group([('visitor_id','in',self.ids)],
                                                       ['visitor_id','page_id','visit_datetime:max'],
                                                       ['visitor_id','page_id'],lazy=False)
        mapped_data={result['visitor_id'][0]:result['page_id'][0]forresultinresultsifresult['page_id']}
        forvisitorinself:
            visitor.last_visited_page_id=mapped_data.get(visitor.id,False)

    @api.depends('last_connection_datetime')
    def_compute_time_statistics(self):
        forvisitorinself:
            visitor.time_since_last_action=_format_time_ago(self.env,(datetime.now()-visitor.last_connection_datetime))
            visitor.is_connected=(datetime.now()-visitor.last_connection_datetime)<timedelta(minutes=5)

    def_check_for_message_composer(self):
        """Purposeofthismethodistoactualizevisitormodelpriortocontacting
        him.Usednotablyforinheritancepurpose,whendealingwithleadsthat
        couldupdatethevisitormodel."""
        returnbool(self.partner_idandself.partner_id.email)

    def_prepare_message_composer_context(self):
        return{
            'default_model':'res.partner',
            'default_res_id':self.partner_id.id,
            'default_partner_ids':[self.partner_id.id],
        }

    defaction_send_mail(self):
        self.ensure_one()
        ifnotself._check_for_message_composer():
            raiseUserError(_("Therearenocontactand/ornoemaillinkedtothisvisitor."))
        visitor_composer_ctx=self._prepare_message_composer_context()
        compose_form=self.env.ref('mail.email_compose_message_wizard_form',False)
        compose_ctx=dict(
            default_use_template=False,
            default_composition_mode='comment',
        )
        compose_ctx.update(**visitor_composer_ctx)
        return{
            'name':_('ContactVisitor'),
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':'mail.compose.message',
            'views':[(compose_form.id,'form')],
            'view_id':compose_form.id,
            'target':'new',
            'context':compose_ctx,
        }

    def_get_visitor_from_request(self,force_create=False):
        """Returnthevisitorassudofromtherequestifthereisavisitor_uuidcookie.
            Itispossiblethatthepartnerhaschangedorhasdisconnected.
            Inthatcasethecookieisstillreferencingtheoldvisitorandneedtobereplaced
            withtheoneofthevisitorreturned!!!."""

        #Thisfunctioncanbecalledinjsonwithmobileapp.
        #Incaseofmobileapp,nouidissetonthejsonRequestenv.
        #Incaseofmultidb,_envisNoneonrequest,andrequest.envunbound.
        ifnotrequest:
            returnNone
        Visitor=self.env['website.visitor'].sudo()
        visitor=Visitor
        access_token=request.httprequest.cookies.get('visitor_uuid')
        ifaccess_token:
            visitor=Visitor.with_context(active_test=False).search([('access_token','=',access_token)])
            #Prefetchaccess_tokenandotherfields.Sinceaccess_tokenhasarestrictedgroupandweaccess
            #anonrestrictedfield(partner_id)firstitisnotfetchedandwillrequireanadditionalquerytoberetrieved.
            visitor.access_token

        ifnotself.env.user._is_public():
            partner_id=self.env.user.partner_id
            ifnotvisitororvisitor.partner_idandvisitor.partner_id!=partner_id:
                #Partnerandnocookieorwrongcookie
                visitor=Visitor.with_context(active_test=False).search([('partner_id','=',partner_id.id)])
        elifvisitorandvisitor.partner_id:
            #CookieassociatedtoaPartner
            visitor=Visitor

        ifvisitorandnotvisitor.timezone:
            tz=self._get_visitor_timezone()
            iftz:
                visitor._update_visitor_timezone(tz)
        ifnotvisitorandforce_create:
            visitor=self._create_visitor()

        returnvisitor

    def_handle_webpage_dispatch(self,response,website_page):
        #getvisitor.Doneheretoavoidhavingtodoitmultipletimesincaseofoverride.
        visitor_sudo=self._get_visitor_from_request(force_create=True)
        ifrequest.httprequest.cookies.get('visitor_uuid','')!=visitor_sudo.access_token:
            expiration_date=datetime.now()+timedelta(days=365)
            response.set_cookie('visitor_uuid',visitor_sudo.access_token,expires=expiration_date)
        self._handle_website_page_visit(website_page,visitor_sudo)

    def_handle_website_page_visit(self,website_page,visitor_sudo):
        """Calledondispatch.Thiswillcreateawebsite.visitorifthehttprequestobject
        isatrackedwebsitepageoratrackedview.Onlyontrackedelementstoavoidhaving
        toomuchoperationsdoneoneverypageorotherhttprequests.
        Note:Thesideeffectisthatthelast_connection_datetimeisupdatedONLYontrackedelements."""
        url=request.httprequest.url
        website_track_values={
            'url':url,
            'visit_datetime':datetime.now(),
        }
        ifwebsite_page:
            website_track_values['page_id']=website_page.id
            domain=[('page_id','=',website_page.id)]
        else:
            domain=[('url','=',url)]
        visitor_sudo._add_tracking(domain,website_track_values)
        ifvisitor_sudo.lang_id.id!=request.lang.id:
            visitor_sudo.write({'lang_id':request.lang.id})

    def_add_tracking(self,domain,website_track_values):
        """Addthetrackandupdatethevisitor"""
        domain=expression.AND([domain,[('visitor_id','=',self.id)]])
        last_view=self.env['website.track'].sudo().search(domain,limit=1)
        ifnotlast_vieworlast_view.visit_datetime<datetime.now()-timedelta(minutes=30):
            website_track_values['visitor_id']=self.id
            self.env['website.track'].create(website_track_values)
        self._update_visitor_last_visit()

    def_create_visitor(self):
        """Createavisitor.Trackingisaddedafterthevisitorhasbeencreated."""
        country_code=request.session.get('geoip',{}).get('country_code',False)
        country_id=request.env['res.country'].sudo().search([('code','=',country_code)],limit=1).idifcountry_codeelseFalse
        vals={
            'lang_id':request.lang.id,
            'country_id':country_id,
            'website_id':request.website.id,
        }

        tz=self._get_visitor_timezone()
        iftz:
            vals['timezone']=tz

        ifnotself.env.user._is_public():
            vals['partner_id']=self.env.user.partner_id.id
            vals['name']=self.env.user.partner_id.name
        returnself.sudo().create(vals)

    def_link_to_partner(self,partner,update_values=None):
        """Linkvisitorstoapartner.Thismethodismeanttobeoverriddenin
        ordertopropagate,ifnecessary,partnerinformationtosubrecords.

        :parampartner:partnerusedtolinksubrecords;
        :paramupdate_values:optionalvaluestoupdatevisitorstolink;
        """
        vals={'name':partner.name}
        ifupdate_values:
            vals.update(update_values)
        self.write(vals)

    def_link_to_visitor(self,target,keep_unique=True):
        """Linkvisitorstotargetvisitors,becausetheyarelinkedtothe
        sameidentity.Purposeismainlytopropagatepartneridentitytosub
        recordstoeasedatabaseupdateanddecidewhattodowith"duplicated".
        THismethodismeanttobeoverriddeninordertoimplementsomespecific
        behaviorlinkedtosubrecordsofduplicatemanagement.

        :paramtarget:mainvisitor,targetoflinkprocess;
        :paramkeep_unique:ifTrue,findawaytomaketargetunique;
        """
        #Linksubrecordsofselftotargetpartner
        iftarget.partner_id:
            self._link_to_partner(target.partner_id)
        #Linksubrecordsofselftotargetvisitor
        self.website_track_ids.write({'visitor_id':target.id})

        ifkeep_unique:
            self.unlink()

        returntarget

    def_cron_archive_visitors(self):
        delay_days=int(self.env['ir.config_parameter'].sudo().get_param('website.visitor.live.days',30))
        deadline=datetime.now()-timedelta(days=delay_days)
        visitors_to_archive=self.env['website.visitor'].sudo().search([('last_connection_datetime','<',deadline)])
        visitors_to_archive.write({'active':False})
        
    def_update_visitor_timezone(self,timezone):
        """Weneedtodothispartheretoavoidconcurrentupdateserror."""
        try:
            withself.env.cr.savepoint():
                query_lock="SELECT*FROMwebsite_visitorwhereid=%sFORNOKEYUPDATENOWAIT"
                self.env.cr.execute(query_lock,(self.id,),log_exceptions=False)
                query="UPDATEwebsite_visitorSETtimezone=%sWHEREid=%s"
                self.env.cr.execute(query,(timezone,self.id),log_exceptions=False)
        exceptException:
            pass

    def_update_visitor_last_visit(self):
        """Weneedtodothispartheretoavoidconcurrentupdateserror."""
        try:
            withself.env.cr.savepoint():
                query_lock="SELECT*FROMwebsite_visitorwhereid=%sFORNOKEYUPDATENOWAIT"
                self.env.cr.execute(query_lock,(self.id,),log_exceptions=False)

                date_now=datetime.now()
                query="UPDATEwebsite_visitorSET"
                ifself.last_connection_datetime<(date_now-timedelta(hours=8)):
                    query+="visit_count=visit_count+1,"
                query+="""
                    active=True,
                    last_connection_datetime=%s
                    WHEREid=%s
                """
                self.env.cr.execute(query,(date_now,self.id),log_exceptions=False)
        exceptException:
            pass

    def_get_visitor_timezone(self):
        tz=request.httprequest.cookies.get('tz')ifrequestelseNone
        iftzinpytz.all_timezones:
            returntz
        elifnotself.env.user._is_public():
            returnself.env.user.tz
        else:
            returnNone
