#-*-coding:utf-8-*-

importcollections
importbabel.dates
importre
importwerkzeug
fromwerkzeug.datastructuresimportOrderedMultiDict
fromwerkzeug.exceptionsimportNotFound

fromastimportliteral_eval
fromcollectionsimportdefaultdict
fromdatetimeimportdatetime,timedelta
fromdateutil.relativedeltaimportrelativedelta

fromflectraimportfields,http,_
fromflectra.addons.http_routing.models.ir_httpimportslug
fromflectra.addons.website.controllers.mainimportQueryURL
fromflectra.addons.event.controllers.mainimportEventController
fromflectra.httpimportrequest
fromflectra.osvimportexpression
fromflectra.tools.miscimportget_lang,format_date
fromflectra.exceptionsimportUserError

classWebsiteEventController(http.Controller):

    defsitemap_event(env,rule,qs):
        ifnotqsorqs.lower()in'/events':
            yield{'loc':'/events'}

    @http.route(['/event','/event/page/<int:page>','/events','/events/page/<int:page>'],type='http',auth="public",website=True,sitemap=sitemap_event)
    defevents(self,page=1,**searches):
        Event=request.env['event.event']
        SudoEventType=request.env['event.type'].sudo()

        searches.setdefault('search','')
        searches.setdefault('date','all')
        searches.setdefault('tags','')
        searches.setdefault('type','all')
        searches.setdefault('country','all')

        website=request.website
        today=fields.Datetime.today()

        defsdn(date):
            returnfields.Datetime.to_string(date.replace(hour=23,minute=59,second=59))

        defsd(date):
            returnfields.Datetime.to_string(date)

        defget_month_filter_domain(filter_name,months_delta):
            first_day_of_the_month=today.replace(day=1)
            filter_string=_('Thismonth')ifmonths_delta==0\
                elseformat_date(request.env,value=today+relativedelta(months=months_delta),
                                 date_format='LLLL',lang_code=get_lang(request.env).code).capitalize()
            return[filter_name,filter_string,[
                ("date_end",">=",sd(first_day_of_the_month+relativedelta(months=months_delta))),
                ("date_begin","<",sd(first_day_of_the_month+relativedelta(months=months_delta+1)))],
                0]

        dates=[
            ['all',_('UpcomingEvents'),[("date_end",">",sd(today))],0],
            ['today',_('Today'),[
                ("date_end",">",sd(today)),
                ("date_begin","<",sdn(today))],
                0],
            get_month_filter_domain('month',0),
            ['old',_('PastEvents'),[
                ("date_end","<",sd(today))],
                0],
        ]

        #searchdomains
        domain_search={'website_specific':website.website_domain()}

        ifsearches['search']:
            domain_search['search']=[('name','ilike',searches['search'])]

        search_tags=self._extract_searched_event_tags(searches)
        ifsearch_tags:
            #Example:Youfilteronage:10-12andactivity:football.
            #Doingitthiswayallowstoonlygeteventswhoaretagged"age:10-12"AND"activity:football".
            #Addanothertag"age:12-15"tothesearchanditwouldfetchtheoneswhoaretagged:
            #("age:10-12"OR"age:12-15")AND"activity:football
            grouped_tags=defaultdict(list)
            fortaginsearch_tags:
                grouped_tags[tag.category_id].append(tag)
            domain_search['tags']=[]
            forgroupingrouped_tags:
                domain_search['tags']=expression.AND([domain_search['tags'],[('tag_ids','in',[tag.idfortagingrouped_tags[group]])]])

        current_date=None
        current_type=None
        current_country=None
        fordateindates:
            ifsearches["date"]==date[0]:
                domain_search["date"]=date[2]
                ifdate[0]!='all':
                    current_date=date[1]

        ifsearches["type"]!='all':
            current_type=SudoEventType.browse(int(searches['type']))
            domain_search["type"]=[("event_type_id","=",int(searches["type"]))]

        ifsearches["country"]!='all'andsearches["country"]!='online':
            current_country=request.env['res.country'].browse(int(searches['country']))
            domain_search["country"]=['|',("country_id","=",int(searches["country"])),("country_id","=",False)]
        elifsearches["country"]=='online':
            domain_search["country"]=[("country_id","=",False)]

        defdom_without(without):
            domain=[]
            forkey,searchindomain_search.items():
                ifkey!=without:
                    domain+=search
            returndomain

        #countbydomainswithoutselfsearch
        fordateindates:
            ifdate[0]!='old':
                date[3]=Event.search_count(dom_without('date')+date[2])

        domain=dom_without('type')

        domain=dom_without('country')
        countries=Event.read_group(domain,["id","country_id"],groupby="country_id",orderby="country_id")
        countries.insert(0,{
            'country_id_count':sum([int(country['country_id_count'])forcountryincountries]),
            'country_id':("all",_("AllCountries"))
        })

        step=12 #Numberofeventsperpage
        event_count=Event.search_count(dom_without("none"))
        pager=website.pager(
            url="/event",
            url_args=searches,
            total=event_count,
            page=page,
            step=step,
            scope=5)

        order='date_begin'
        ifsearches.get('date','all')=='old':
            order='date_begindesc'
        order='is_publisheddesc,'+order
        events=Event.search(dom_without("none"),limit=step,offset=pager['offset'],order=order)

        keep=QueryURL('/event',**{key:valueforkey,valueinsearches.items()if(key=='search'orvalue!='all')})

        values={
            'current_date':current_date,
            'current_country':current_country,
            'current_type':current_type,
            'event_ids':events, #event_idsusedinwebsite_event_tracksowekeepnameasitis
            'dates':dates,
            'categories':request.env['event.tag.category'].search([]),
            'countries':countries,
            'pager':pager,
            'searches':searches,
            'search_tags':search_tags,
            'keep':keep,
        }

        ifsearches['date']=='old':
            #theonlywaytodisplaythiscontentistosetdate=oldsoitmustbecanonical
            values['canonical_params']=OrderedMultiDict([('date','old')])

        returnrequest.render("website_event.index",values)

    @http.route(['''/event/<model("event.event"):event>/page/<path:page>'''],type='http',auth="public",website=True,sitemap=False)
    defevent_page(self,event,page,**post):
        ifnotevent.can_access_from_current_website():
            raisewerkzeug.exceptions.NotFound()

        values={
            'event':event,
        }

        if'.'notinpage:
            page='website_event.%s'%page

        try:
            #EveryeventpageviewshouldhaveitsownSEO.
            values['seo_object']=request.website.get_template(page)
            values['main_object']=event
        exceptValueError:
            #pagenotfound
            values['path']=re.sub(r"^website_event\.",'',page)
            values['from_template']='website_event.default_page' #.strip('website_event.')
            page=request.website.is_publisher()and'website.page_404'or'http_routing.404'

        returnrequest.render(page,values)

    @http.route(['''/event/<model("event.event"):event>'''],type='http',auth="public",website=True,sitemap=True)
    defevent(self,event,**post):
        ifnotevent.can_access_from_current_website():
            raisewerkzeug.exceptions.NotFound()

        ifevent.menu_idandevent.menu_id.child_id:
            target_url=event.menu_id.child_id[0].url
        else:
            target_url='/event/%s/register'%str(event.id)
        ifpost.get('enable_editor')=='1':
            target_url+='?enable_editor=1'
        returnrequest.redirect(target_url)

    @http.route(['''/event/<model("event.event"):event>/register'''],type='http',auth="public",website=True,sitemap=False)
    defevent_register(self,event,**post):
        ifnotevent.can_access_from_current_website():
            raisewerkzeug.exceptions.NotFound()

        values=self._prepare_event_register_values(event,**post)
        returnrequest.render("website_event.event_description_full",values)

    def_prepare_event_register_values(self,event,**post):
        """Returntherequirevaluestorenderthetemplate."""
        urls=event._get_event_resource_urls()
        return{
            'event':event,
            'main_object':event,
            'range':range,
            'google_url':urls.get('google_url'),
            'iCal_url':urls.get('iCal_url'),
        }

    @http.route('/event/add_event',type='json',auth="user",methods=['POST'],website=True)
    defadd_event(self,event_name="NewEvent",**kwargs):
        event=self._add_event(event_name,request.context)
        return"/event/%s/register?enable_editor=1"%slug(event)

    def_add_event(self,event_name=None,context=None,**kwargs):
        ifnotevent_name:
            event_name=_("NewEvent")
        date_begin=datetime.today()+timedelta(days=(14))
        vals={
            'name':event_name,
            'date_begin':fields.Date.to_string(date_begin),
            'date_end':fields.Date.to_string((date_begin+timedelta(days=(1)))),
            'seats_available':1000,
            'website_id':request.website.id,
        }
        returnrequest.env['event.event'].with_context(contextor{}).create(vals)

    defget_formated_date(self,event):
        start_date=fields.Datetime.from_string(event.date_begin).date()
        end_date=fields.Datetime.from_string(event.date_end).date()
        month=babel.dates.get_month_names('abbreviated',locale=get_lang(event.env).code)[start_date.month]
        return('%s%s%s')%(month,start_date.strftime("%e"),(end_date!=start_dateand("-"+end_date.strftime("%e"))or""))

    @http.route('/event/get_country_event_list',type='json',auth='public',website=True)
    defget_country_events(self,**post):
        Event=request.env['event.event']
        country_code=request.session['geoip'].get('country_code')
        result={'events':[],'country':False}
        events=None
        domain=request.website.website_domain()
        ifcountry_code:
            country=request.env['res.country'].search([('code','=',country_code)],limit=1)
            events=Event.search(domain+['|',('address_id','=',None),('country_id.code','=',country_code),('date_begin','>=','%s00:00:00'%fields.Date.today())],order="date_begin")
        ifnotevents:
            events=Event.search(domain+[('date_begin','>=','%s00:00:00'%fields.Date.today())],order="date_begin")
        foreventinevents:
            ifcountry_codeandevent.country_id.code==country_code:
                result['country']=country
            result['events'].append({
                "date":self.get_formated_date(event),
                "event":event,
                "url":event.website_url})
        returnrequest.env['ir.ui.view']._render_template("website_event.country_events_list",result)

    def_process_tickets_form(self,event,form_details):
        """Processposteddataaboutticketorder.Genericticketaresupported
        foreventwithouttickets(genericregistration).

        :return:listoforderperticket:[{
            'id':ifofticketifany(0ifnoticket),
            'ticket':browserecordofticketifany(Noneifnoticket),
            'name':ticketname(orgeneric'Registration'nameifnoticket),
            'quantity':numberofregistrationsforthatticket,
        },{...}]
        """
        ticket_order={}
        forkey,valueinform_details.items():
            registration_items=key.split('nb_register-')
            iflen(registration_items)!=2:
                continue
            ticket_order[int(registration_items[1])]=int(value)

        ticket_dict=dict((ticket.id,ticket)forticketinrequest.env['event.event.ticket'].search([
            ('id','in',[tidfortidinticket_order.keys()iftid]),
            ('event_id','=',event.id)
        ]))

        return[{
            'id':tidifticket_dict.get(tid)else0,
            'ticket':ticket_dict.get(tid),
            'name':ticket_dict[tid]['name']ifticket_dict.get(tid)else_('Registration'),
            'quantity':count,
        }fortid,countinticket_order.items()ifcount]

    @http.route(['/event/<model("event.event"):event>/registration/new'],type='json',auth="public",methods=['POST'],website=True)
    defregistration_new(self,event,**post):
        ifnotevent.can_access_from_current_website():
            raisewerkzeug.exceptions.NotFound()

        tickets=self._process_tickets_form(event,post)
        availability_check=True
        ifevent.seats_limited:
            ordered_seats=0
            forticketintickets:
                ordered_seats+=ticket['quantity']
            ifevent.seats_available<ordered_seats:
                availability_check=False
        ifnottickets:
            returnFalse
        returnrequest.env['ir.ui.view']._render_template("website_event.registration_attendee_details",{'tickets':tickets,'event':event,'availability_check':availability_check})

    def_process_attendees_form(self,event,form_details):
        """Processdatapostedfromtheattendeedetailsform.

        :paramform_details:posteddatafromfrontendregistrationform,like
            {'1-name':'r','1-email':'r@r.com','1-phone':'','1-event_ticket_id':'1'}
        """
        allowed_fields=request.env['event.registration']._get_website_registration_allowed_fields()
        registration_fields={key:vforkey,vinrequest.env['event.registration']._fields.items()ifkeyinallowed_fields}
        forticket_idinlist(filter(lambdax:xisnotNone,[form_details[field]if'event_ticket_id'infieldelseNoneforfieldinform_details.keys()])):
            ifint(ticket_id)notinevent.event_ticket_ids.idsandlen(event.event_ticket_ids.ids)>0:
                raiseUserError(_("Thisticketisnotavailableforsaleforthisevent"))
        registrations={}
        global_values={}
        forkey,valueinform_details.items():
            counter,attr_name=key.split('-',1)
            field_name=attr_name.split('-')[0]
            iffield_namenotinregistration_fields:
                continue
            elifisinstance(registration_fields[field_name],(fields.Many2one,fields.Integer)):
                value=int(value)orFalse #0isconsideredasavoidmany2oneakaFalse
            else:
                value=value

            ifcounter=='0':
                global_values[attr_name]=value
            else:
                registrations.setdefault(counter,dict())[attr_name]=value
        forkey,valueinglobal_values.items():
            forregistrationinregistrations.values():
                registration[key]=value

        returnlist(registrations.values())

    def_create_attendees_from_registration_post(self,event,registration_data):
        """Alsotrytosetavisitor(fromrequest)and
        apartner(ifvisitorlinkedtoauserforexample).Purposeistogather
        asmuchinformationsaspossible,notablytoeasefuturecommunications.
        Alsotrytoupdatevisitorinformationsbasedonregistrationinfo."""
        visitor_sudo=request.env['website.visitor']._get_visitor_from_request(force_create=True)
        visitor_sudo._update_visitor_last_visit()
        visitor_values={}

        registrations_to_create=[]
        forregistration_valuesinregistration_data:
            registration_values['event_id']=event.id
            ifnotregistration_values.get('partner_id')andvisitor_sudo.partner_id:
                registration_values['partner_id']=visitor_sudo.partner_id.id
            elifnotregistration_values.get('partner_id'):
                registration_values['partner_id']=request.env.user.partner_id.id

            ifvisitor_sudo:
                #registrationmaygiveanametothevisitor,yay
                ifregistration_values.get('name')andnotvisitor_sudo.nameandnotvisitor_values.get('name'):
                    visitor_values['name']=registration_values['name']
                #updateregistrationbasedonvisitor
                registration_values['visitor_id']=visitor_sudo.id

            registrations_to_create.append(registration_values)

        ifvisitor_values:
            visitor_sudo.write(visitor_values)

        returnrequest.env['event.registration'].sudo().create(registrations_to_create)

    @http.route(['''/event/<model("event.event"):event>/registration/confirm'''],type='http',auth="public",methods=['POST'],website=True)
    defregistration_confirm(self,event,**post):
        ifnotevent.can_access_from_current_website():
            raisewerkzeug.exceptions.NotFound()

        registrations=self._process_attendees_form(event,post)
        attendees_sudo=self._create_attendees_from_registration_post(event,registrations)

        returnrequest.render("website_event.registration_complete",
            self._get_registration_confirm_values(event,attendees_sudo))

    def_get_registration_confirm_values(self,event,attendees_sudo):
        urls=event._get_event_resource_urls()
        return{
            'attendees':attendees_sudo,
            'event':event,
            'google_url':urls.get('google_url'),
            'iCal_url':urls.get('iCal_url')
        }

    def_extract_searched_event_tags(self,searches):
        tags=request.env['event.tag']
        ifsearches.get('tags'):
            try:
                tag_ids=literal_eval(searches['tags'])
            except:
                pass
            else:
                #performasearchtofilteronexisting/validtagsimplicitely+applyrulesoncolor
                tags=request.env['event.tag'].search([('id','in',tag_ids)])
        returntags
