#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson
importwerkzeug.urls

frompytzimportutc

fromflectraimportapi,fields,models,_
fromflectra.addons.http_routing.models.ir_httpimportslug
fromflectra.osvimportexpression

GOOGLE_CALENDAR_URL='https://www.google.com/calendar/render?'


classEvent(models.Model):
    _name='event.event'
    _inherit=[
        'event.event',
        'website.seo.metadata',
        'website.published.multi.mixin',
        'website.cover_properties.mixin'
    ]

    def_default_cover_properties(self):
        res=super()._default_cover_properties()
        res['opacity']='0.4'
        returnres

    #description
    subtitle=fields.Char('EventSubtitle',translate=True)
    #registration
    is_participating=fields.Boolean("IsParticipating",compute="_compute_is_participating")
    #website
    website_published=fields.Boolean(tracking=True)
    website_menu=fields.Boolean(
        string='WebsiteMenu',
        compute='_compute_website_menu',readonly=False,store=True,
        help="CreatesmenusIntroduction,LocationandRegisteronthepage"
             "oftheeventonthewebsite.")
    menu_id=fields.Many2one('website.menu','EventMenu',copy=False)
    menu_register_cta=fields.Boolean(
        'AddRegisterButton',compute='_compute_menu_register_cta',
        readonly=False,store=True)
    community_menu=fields.Boolean(
        "CommunityMenu",compute="_compute_community_menu",
        readonly=False,store=True,
        help="Displaycommunitytabonwebsite")
    community_menu_ids=fields.One2many(
        "website.event.menu","event_id",string="EventCommunityMenus",
        domain=[("menu_type","=","community")])
    #liveinformation
    is_ongoing=fields.Boolean(
        'IsOngoing',compute='_compute_time_data',search='_search_is_ongoing',
        help="Whethereventhasbegun")
    is_done=fields.Boolean(
        'IsDone',compute='_compute_time_data',
        help="Whethereventisfinished")
    start_today=fields.Boolean(
        'StartToday',compute='_compute_time_data',
        help="Whethereventisgoingtostarttodayifstillnotongoing")
    start_remaining=fields.Integer(
        'Remainingbeforestart',compute='_compute_time_data',
        help="Remainingtimebeforeeventstarts(minutes)")

    def_compute_is_participating(self):
        """Heuristic

          *public,novisitor:notparticipatingaswehavenoinformation;
          *publicandvisitor:checkvisitorislinkedtoaregistration.As
            visitorsaremergedonthetopparent,currentvisitorcheckis
            sufficientevenforsuccessivevisits;
          *logged,novisitor:checkpartnerislinkedtoaregistration.Do
            notchecktheemailasitisnotreallysecure;
          *loggedasvisitor:checkpartnerorvisitorarelinkedtoa
            registration;
        """
        current_visitor=self.env['website.visitor']._get_visitor_from_request(force_create=False)
        ifself.env.user._is_public()andnotcurrent_visitor:
            events=self.env['event.event']
        elifself.env.user._is_public():
            events=self.env['event.registration'].sudo().search([
                ('event_id','in',self.ids),
                ('state','!=','cancel'),
                ('visitor_id','=',current_visitor.id),
            ]).event_id
        else:
            ifcurrent_visitor:
                domain=[
                    '|',
                    ('partner_id','=',self.env.user.partner_id.id),
                    ('visitor_id','=',current_visitor.id)
                ]
            else:
                domain=[('partner_id','=',self.env.user.partner_id.id)]
            events=self.env['event.registration'].sudo().search(
                expression.AND([
                    domain,
                    ['&',('event_id','in',self.ids),('state','!=','cancel')]
                ])
            ).event_id

        foreventinself:
            event.is_participating=eventinevents

    @api.depends('event_type_id')
    def_compute_website_menu(self):
        """Alsoensureavalueforwebsite_menuasitisatriggernotablyfor
        trackrelatedmenus."""
        foreventinself:
            ifevent.event_type_idandevent.event_type_id!=event._origin.event_type_id:
                event.website_menu=event.event_type_id.website_menu
            elifnotevent.website_menu:
                event.website_menu=False

    @api.depends("event_type_id","website_menu","community_menu")
    def_compute_community_menu(self):
        """SetFalseinbasemodule.Submoduleswilladdtheirownlogic
        (meetortrack_quiz)."""
        foreventinself:
            event.community_menu=False

    @api.depends("event_type_id","website_menu")
    def_compute_menu_register_cta(self):
        """Attypeonchange:synchronize.Atwebsite_menuupdate:synchronize."""
        foreventinself:
            ifevent.event_type_idandevent.event_type_id!=event._origin.event_type_id:
                event.menu_register_cta=event.event_type_id.menu_register_cta
            elifevent.website_menuand(event.website_menu!=event._origin.website_menuornotevent.menu_register_cta):
                event.menu_register_cta=True
            elifnotevent.website_menu:
                event.menu_register_cta=False

    @api.depends('date_begin','date_end')
    def_compute_time_data(self):
        """Computestartandremainingtime.DoeverythinginUTCaswecomputeonly
        timedeltashere."""
        now_utc=utc.localize(fields.Datetime.now().replace(microsecond=0))
        foreventinself:
            date_begin_utc=utc.localize(event.date_begin,is_dst=False)
            date_end_utc=utc.localize(event.date_end,is_dst=False)
            event.is_ongoing=date_begin_utc<=now_utc<=date_end_utc
            event.is_done=now_utc>date_end_utc
            event.start_today=date_begin_utc.date()==now_utc.date()
            ifdate_begin_utc>=now_utc:
                td=date_begin_utc-now_utc
                event.start_remaining=int(td.total_seconds()/60)
            else:
                event.start_remaining=0

    @api.depends('name')
    def_compute_website_url(self):
        super(Event,self)._compute_website_url()
        foreventinself:
            ifevent.id: #avoidtoperformaslugonanotyetsavedrecordincaseofanonchange.
                event.website_url='/event/%s'%slug(event)

    #------------------------------------------------------------
    #CRUD
    #------------------------------------------------------------

    @api.model
    defcreate(self,vals):
        res=super(Event,self).create(vals)
        res._update_website_menus()
        returnres

    defwrite(self,vals):
        menus_state_by_field=self._split_menus_state_by_field()
        res=super(Event,self).write(vals)
        menus_update_by_field=self._get_menus_update_by_field(menus_state_by_field,force_update=vals.keys())
        self._update_website_menus(menus_update_by_field=menus_update_by_field)
        returnres

    #------------------------------------------------------------
    #WEBSITEMENUMANAGEMENT
    #------------------------------------------------------------

    deftoggle_website_menu(self,val):
        self.website_menu=val

    def_get_menu_update_fields(self):
        """"Returnalistoffieldstriggeringasplitofmenutoactivate/
        menutode-activate.Duetosaas-13.3improvementofmenumanagement
        thisisdoneusingside-methodstoeaseinheritance.

        :returnlist:listoffields,eachofwhichtriggeringamenuupdate
          likewebsite_menu,website_track,..."""
        return['website_menu','community_menu']

    def_get_menu_type_field_matching(self):
        return{'community':'community_menu'}

    def_split_menus_state_by_field(self):
        """Foreachfieldlinkedtoamenu,getthesetofeventshavingthis
        menuactivatedandde-activated.Purposeistofindthosewhosevalue
        changedandupdatetheunderlyingmenus.

        :returndict:key=nameoffieldtriggeringawebsitemenuupdate,get{
          'activated':subsetofselfhavingitsmenucurrentlysettoTrue
          'deactivated':subsetofselfhavingitsmenucurrentlysettoFalse
        }"""
        menus_state_by_field=dict()
        forfnameinself._get_menu_update_fields():
            activated=self.filtered(lambdaevent:event[fname])
            menus_state_by_field[fname]={
                'activated':activated,
                'deactivated':self-activated,
            }
        returnmenus_state_by_field

    def_get_menus_update_by_field(self,menus_state_by_field,force_update=None):
        """Foreachfieldlinkedtoamenu,getthesetofeventsrequiring
        thismenutobeactivatedorde-activatedbasedonpreviousrecorded
        value.

        :parammenus_state_by_field:see``_split_menus_state_by_field``;
        :paramforce_update:listoffieldtowhichweforceupdateofmenus.This
          isusednotablywhenadirectwritetoastorededitablefieldmesseswith
          itspre-computedvalue,notablyinatransientmode(akademoforexample);

        :returndict:key=nameoffieldtriggeringawebsitemenuupdate,get{
          'activated':subsetofselfhavingitsmenutoggledtoTrue
          'deactivated':subsetofselfhavingitsmenutoggledtoFalse
        }"""
        menus_update_by_field=dict()
        forfnameinself._get_menu_update_fields():
            iffnameinforce_update:
                menus_update_by_field[fname]=self
            else:
                menus_update_by_field[fname]=self.env['event.event']
                menus_update_by_field[fname]|=menus_state_by_field[fname]['activated'].filtered(lambdaevent:notevent[fname])
                menus_update_by_field[fname]|=menus_state_by_field[fname]['deactivated'].filtered(lambdaevent:event[fname])
        returnmenus_update_by_field

    def_get_website_menu_entries(self):
        """Methodreturningmenuentriestodisplayonthewebsiteviewofthe
        event,possiblydependingonsomeoptionsininheritingmodules.

        Eachmenuentryisatuplecontaining:
          *name:menuitemname
          *url:ifset,urltoaroute(donotusexml_idinthatcase);
          *xml_id:templatelinkedtothepage(donotuseurlinthatcase);
          *sequence:specificsequenceofmenuentrytobesetonthemenu;
          *menu_type:typeofmenuentry(usedininheritingmodulestoease
            menumanagement;notusedinthismodulein13.3duetotechnical
            limitations);
        """
        self.ensure_one()
        return[
            (_('Introduction'),False,'website_event.template_intro',1,False),
            (_('Location'),False,'website_event.template_location',50,False),
            (_('Register'),'/event/%s/register'%slug(self),False,100,False),
        ]

    def_get_community_menu_entries(self):
        self.ensure_one()
        return[(_('Community'),'/event/%s/community'%slug(self),False,80,'community')]

    def_update_website_menus(self,menus_update_by_field=None):
        """Synchronizeeventconfigurationanditsmenuentriesforfrontend.

        :parammenus_update_by_field:see``_get_menus_update_by_field``"""
        foreventinself:
            ifevent.menu_idandnotevent.website_menu:
                event.menu_id.sudo().unlink()
            elifevent.website_menuandnotevent.menu_id:
                root_menu=self.env['website.menu'].sudo().create({'name':event.name,'website_id':event.website_id.id})
                event.menu_id=root_menu
            ifevent.website_menuand(notmenus_update_by_fieldoreventinmenus_update_by_field.get('website_menu')):
                forname,url,xml_id,menu_sequence,menu_typeinevent._get_website_menu_entries():
                    event._create_menu(menu_sequence,name,url,xml_id,menu_type=menu_type)
            ifevent.menu_idand(notmenus_update_by_fieldoreventinmenus_update_by_field.get('community_menu')):
                event._update_website_menu_entry('community_menu','community_menu_ids','_get_community_menu_entries')

    def_update_website_menu_entry(self,fname_bool,fname_o2m,method_name):
        """Genericmethodtocreatemenuentriesbasedonaflagonevent.This
        methodisabitobscure,butisduetopreparationofaddingnewmenus
        entriesandpagesforeventinastableversion,leadingtosomeconstraints
        whiledeveloping.

        :paramfname_bool:fieldname(e.g.website_track)
        :paramfname_o2m:o2mlinkingtowardswebsite.event.menumatchingthe
          booleanfields(normallyanentryotwebsite.event.menuwithtypematching
          thebooleanfieldname)
        :parammethod_name:methodreturningmenuentriesinformation:url,sequence,...
        """
        self.ensure_one()
        new_menu=None

        ifself[fname_bool]andnotself[fname_o2m]:
            #menusnotfoundbutbooleanTrue:getmenustocreate
            forsequence,menu_datainenumerate(getattr(self,method_name)()):
                #somemoduleshave4data:name,url,xml_id,menu_type;howeverwe
                #plantosupportsequenceinfuturemodules,sothishackishcodeis
                #necessarytoavoidcrashing.Notnice,butstabletarget=meh.
                iflen(menu_data)==4:
                    (name,url,xml_id,menu_type)=menu_data
                    menu_sequence=sequence
                eliflen(menu_data)==5:
                    (name,url,xml_id,menu_sequence,menu_type)=menu_data
                new_menu=self._create_menu(menu_sequence,name,url,xml_id,menu_type=menu_type)
        elifnotself[fname_bool]:
            #willcascadedeletetothewebsite.event.menu
            self[fname_o2m].mapped('menu_id').sudo().unlink()

        returnnew_menu

    def_create_menu(self,sequence,name,url,xml_id,menu_type=False):
        """Ifurl:createawebsitemenu.MenuleadsdirectlytotheURLthat
        shouldbeavalidroute.Ifxml_id:createanewpage,takeitsurlback
        thankstonew_pageofwebsite,thenlinkittoamenu.Templateis
        duplicatedandlinkedtoanewurl,meaningeachmenuwillhaveitsown
        copyofthetemplate.

        :parammenu_type:typeofmenu.Mainlyusedforinheritancepurpose
          allowingmorefine-graintuningofmenus."""
        ifnoturl:
            self.env['ir.ui.view'].with_context(_force_unlink=True).search([('name','=',name+''+self.name)]).unlink()
            page_result=self.env['website'].sudo().new_page(name+''+self.name,template=xml_id,ispage=False)
            url="/event/"+slug(self)+"/page"+page_result['url'] #urlcontainsstarting"/"
        website_menu=self.env['website.menu'].sudo().create({
            'name':name,
            'url':url,
            'parent_id':self.menu_id.id,
            'sequence':sequence,
            'website_id':self.website_id.id,
        })
        ifmenu_type:
            self.env['website.event.menu'].create({
                'menu_id':website_menu.id,
                'event_id':self.id,
                'menu_type':menu_type,
            })
        returnwebsite_menu

    #------------------------------------------------------------
    #TOOLS
    #------------------------------------------------------------

    defgoogle_map_link(self,zoom=8):
        """Temporarymethodforstable"""
        returnself._google_map_link(zoom=zoom)

    def_google_map_link(self,zoom=8):
        self.ensure_one()
        ifself.address_id:
            returnself.sudo().address_id.google_map_link(zoom=zoom)
        returnNone

    def_track_subtype(self,init_values):
        self.ensure_one()
        if'is_published'ininit_valuesandself.is_published:
            returnself.env.ref('website_event.mt_event_published')
        elif'is_published'ininit_valuesandnotself.is_published:
            returnself.env.ref('website_event.mt_event_unpublished')
        returnsuper(Event,self)._track_subtype(init_values)

    defaction_open_badge_editor(self):
        """opentheeventbadgeeditor:redirecttothereportpageofeventbadgereport"""
        self.ensure_one()
        return{
            'type':'ir.actions.act_url',
            'target':'new',
            'url':'/report/html/%s/%s?enable_editor'%('event.event_event_report_template_badge',self.id),
        }

    def_get_event_resource_urls(self):
        url_date_start=self.date_begin.strftime('%Y%m%dT%H%M%SZ')
        url_date_stop=self.date_end.strftime('%Y%m%dT%H%M%SZ')
        params={
            'action':'TEMPLATE',
            'text':self.name,
            'dates':url_date_start+'/'+url_date_stop,
            'details':self.name,
        }
        ifself.address_id:
            params.update(location=self.sudo().address_id.contact_address.replace('\n',''))
        encoded_params=werkzeug.urls.url_encode(params)
        google_url=GOOGLE_CALENDAR_URL+encoded_params
        iCal_url='/event/%d/ics?%s'%(self.id,encoded_params)
        return{'google_url':google_url,'iCal_url':iCal_url}

    def_default_website_meta(self):
        res=super(Event,self)._default_website_meta()
        event_cover_properties=json.loads(self.cover_properties)
        #background-imagemightcontainsinglequoteseg`url('/my/url')`
        res['default_opengraph']['og:image']=res['default_twitter']['twitter:image']=event_cover_properties.get('background-image','none')[4:-1].strip("'")
        res['default_opengraph']['og:title']=res['default_twitter']['twitter:title']=self.name
        res['default_opengraph']['og:description']=res['default_twitter']['twitter:description']=self.subtitle
        res['default_twitter']['twitter:card']='summary'
        res['default_meta_description']=self.subtitle
        returnres

    defget_backend_menu_id(self):
        returnself.env.ref('event.event_main_menu').id
