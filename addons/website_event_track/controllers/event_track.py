#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromastimportliteral_eval
fromdatetimeimporttimedelta
frompytzimporttimezone,utc
fromwerkzeug.exceptionsimportForbidden,NotFound

importbabel
importbabel.dates
importbase64
importpytz

fromflectraimportexceptions,http,fields,_
fromflectra.httpimportrequest
fromflectra.osvimportexpression
fromflectra.toolsimportis_html_empty,plaintext2html
fromflectra.tools.miscimportbabel_locale_parse


classEventTrackController(http.Controller):

    def_get_event_tracks_base_domain(self,event):
        """Basedomainfordisplayingtracks.Restricttoacceptedorpublished
        tracksforpeoplenotmanagingevents.Unpublishedtracksmaybedisplayed
        butnotreachableforteasingpurpose."""
        search_domain_base=[
            ('event_id','=',event.id),
        ]
        ifnotrequest.env.user.has_group('event.group_event_user'):
            search_domain_base=expression.AND([
                search_domain_base,
                ['|',('is_published','=',True),('is_accepted','=',True)]
            ])
        returnsearch_domain_base

    #------------------------------------------------------------
    #TRACKLISTVIEW
    #------------------------------------------------------------

    @http.route([
        '''/event/<model("event.event"):event>/track''',
        '''/event/<model("event.event"):event>/track/tag/<model("event.track.tag"):tag>'''
    ],type='http',auth="public",website=True,sitemap=False)
    defevent_tracks(self,event,tag=None,**searches):
        """Mainroute

        :paramevent:eventwhosetracksareabouttobedisplayed;
        :paramtag:deprecated:searchforaspecifictag
        :paramsearches:frontendsearchdict,containing

          *'search':searchstring;
          *'tags':listoftagIDsforfiltering;
        """
        ifnotevent.can_access_from_current_website():
            raiseNotFound()

        returnrequest.render(
            "website_event_track.tracks_session",
            self._event_tracks_get_values(event,tag=tag,**searches)
        )

    def_event_tracks_get_values(self,event,tag=None,**searches):
        #initandprocesssearchterms
        searches.setdefault('search','')
        searches.setdefault('search_wishlist','')
        searches.setdefault('tags','')
        search_domain=self._get_event_tracks_base_domain(event)

        #searchoncontent
        ifsearches.get('search'):
            search_domain=expression.AND([
                search_domain,
                [('name','ilike',searches['search'])]
            ])

        #searchontags
        search_tags=self._get_search_tags(searches['tags'])
        ifnotsearch_tagsandtag: #backwardcompatibility
            search_tags=tag
        ifsearch_tags:
            #Example:Youfilteronage:10-12andactivity:football.
            #Doingitthiswayallowstoonlygeteventswhoaretagged"age:10-12"AND"activity:football".
            #Addanothertag"age:12-15"tothesearchanditwouldfetchtheoneswhoaretagged:
            #("age:10-12"OR"age:12-15")AND"activity:football
            grouped_tags=dict()
            forsearch_taginsearch_tags:
                grouped_tags.setdefault(search_tag.category_id,list()).append(search_tag)
            search_domain_items=[
                [('tag_ids','in',[tag.idfortagingrouped_tags[group]])]
                forgroupingrouped_tags
            ]
            search_domain=expression.AND([
                search_domain,
                *search_domain_items
            ])

        #fetchdatatodisplaywithTZsetforbotheventandtracks
        now_tz=utc.localize(fields.Datetime.now().replace(microsecond=0),is_dst=False).astimezone(timezone(event.date_tz))
        today_tz=now_tz.date()
        event=event.with_context(tz=event.date_tzor'UTC')
        tracks_sudo=event.env['event.track'].sudo().search(search_domain,order='dateasc')
        tag_categories=request.env['event.track.tag.category'].sudo().search([])

        #filteronwishlist(aspostprocessingduetocostlysearchonis_reminder_on)
        ifsearches.get('search_wishlist'):
            tracks_sudo=tracks_sudo.filtered(lambdatrack:track.is_reminder_on)

        #organizecategoriesfordisplay:announced,live,soonandday-based
        tracks_announced=tracks_sudo.filtered(lambdatrack:nottrack.date)
        tracks_wdate=tracks_sudo-tracks_announced
        date_begin_tz_all=list(set(
            dt.date()
            fordtinself._get_dt_in_event_tz(tracks_wdate.mapped('date'),event)
        ))
        date_begin_tz_all.sort()
        tracks_sudo_live=tracks_wdate.filtered(lambdatrack:track.is_publishedandtrack.is_track_live)
        tracks_sudo_soon=tracks_wdate.filtered(lambdatrack:track.is_publishedandnottrack.is_track_liveandtrack.is_track_soon)
        tracks_by_day=[]
        fordisplay_dateindate_begin_tz_all:
            matching_tracks=tracks_wdate.filtered(lambdatrack:self._get_dt_in_event_tz([track.date],event)[0].date()==display_date)
            tracks_by_day.append({'date':display_date,'name':display_date,'tracks':matching_tracks})
        iftracks_announced:
            tracks_announced=tracks_announced.sorted('wishlisted_by_default',reverse=True)
            tracks_by_day.append({'date':False,'name':_('Comingsoon'),'tracks':tracks_announced})

        #returnrenderingvalues
        return{
            #eventinformation
            'event':event,
            'main_object':event,
            #tracksdisplayinformation
            'tracks':tracks_sudo,
            'tracks_by_day':tracks_by_day,
            'tracks_live':tracks_sudo_live,
            'tracks_soon':tracks_sudo_soon,
            'today_tz':today_tz,
            #searchinformation
            'searches':searches,
            'search_key':searches['search'],
            'search_wishlist':searches['search_wishlist'],
            'search_tags':search_tags,
            'tag_categories':tag_categories,
            #environment
            'is_html_empty':is_html_empty,
            'hostname':request.httprequest.host.split(':')[0],
            'user_event_manager':request.env.user.has_group('event.group_event_manager'),
        }

    #------------------------------------------------------------
    #AGENDAVIEW
    #------------------------------------------------------------

    @http.route(['''/event/<model("event.event"):event>/agenda'''],type='http',auth="public",website=True,sitemap=False)
    defevent_agenda(self,event,tag=None,**post):
        ifnotevent.can_access_from_current_website():
            raiseNotFound()

        event=event.with_context(tz=event.date_tzor'UTC')
        vals={
            'event':event,
            'main_object':event,
            'tag':tag,
            'user_event_manager':request.env.user.has_group('event.group_event_manager'),
        }

        vals.update(self._prepare_calendar_values(event))

        returnrequest.render("website_event_track.agenda_online",vals)

    def_prepare_calendar_values(self,event):
        """
         Overridethatshouldcompletelyreplaceoriginalmethodinv14.

        Thismethodsslittheday(maxendtime-minstarttime)into15minutestimeslots.
        Foreachtimeslot,weassignthetracksthatstartatthisspecifictimeslot,andweaddthenumber
        oftimeslotthatthetrackcovers(trackduration/15min)
        Thecalendarwillbedividedintorowsof15min,andthetalkswillcoverthecorrespondingnumberofrows
        (15minslots).
        """
        event=event.with_context(tz=event.date_tzor'UTC')
        local_tz=pytz.timezone(event.date_tzor'UTC')
        lang_code=request.env.context.get('lang')
        event_track_ids=self._event_agenda_get_tracks(event)

        locations=list(set(track.location_idfortrackinevent_track_ids))
        locations.sort(key=lambdax:x.id)

        #Firstsplitdaybyday(basedonstarttime)
        time_slots_by_tracks={track:self._split_track_by_days(track,local_tz)fortrackinevent_track_ids}

        #extractallthetrackstimeslots
        track_time_slots=set().union(*(time_slot.keys()fortime_slotin[time_slotsfortime_slotsintime_slots_by_tracks.values()]))

        #extractuniquedays
        days=list(set(time_slot.date()fortime_slotintrack_time_slots))
        days.sort()

        #Createthedictthatcontainsthetracksatthecorrecttime_slots/locationscoordinates
        tracks_by_days=dict.fromkeys(days,0)
        time_slots_by_day=dict((day,dict(start=set(),end=set()))fordayindays)
        tracks_by_rounded_times=dict((time_slot,dict((location,{})forlocationinlocations))fortime_slotintrack_time_slots)
        fortrack,time_slotsintime_slots_by_tracks.items():
            start_date=fields.Datetime.from_string(track.date).replace(tzinfo=pytz.utc).astimezone(local_tz)
            end_date=start_date+timedelta(hours=(track.durationor0.25))

            fortime_slot,durationintime_slots.items():
                tracks_by_rounded_times[time_slot][track.location_id][track]={
                    'rowspan':duration, #rowspan
                    'start_date':self._get_locale_time(start_date,lang_code),
                    'end_date':self._get_locale_time(end_date,lang_code),
                    'occupied_cells':self._get_occupied_cells(track,duration,locations,local_tz)
                }

                #getallthetimeslotsbydaytodeterminethemaxdurationofaday.
                day=time_slot.date()
                time_slots_by_day[day]['start'].add(time_slot)
                time_slots_by_day[day]['end'].add(time_slot+timedelta(minutes=15*duration))
                tracks_by_days[day]+=1

        #splitdaysinto15minutestimeslots
        global_time_slots_by_day=dict((day,{})fordayindays)
        forday,time_slotsintime_slots_by_day.items():
            start_time_slot=min(time_slots['start'])
            end_time_slot=max(time_slots['end'])

            time_slots_count=int(((end_time_slot-start_time_slot).total_seconds()/3600)*4)
            current_time_slot=start_time_slot
            foriinrange(0,time_slots_count+1):
                global_time_slots_by_day[day][current_time_slot]=tracks_by_rounded_times.get(current_time_slot,{})
                global_time_slots_by_day[day][current_time_slot]['formatted_time']=self._get_locale_time(current_time_slot,lang_code)
                current_time_slot=current_time_slot+timedelta(minutes=15)

        #countthenumberoftracksbydays
        tracks_by_days=dict.fromkeys(days,0)
        fortrackinevent_track_ids:
            track_day=fields.Datetime.from_string(track.date).replace(tzinfo=pytz.utc).astimezone(local_tz).date()
            tracks_by_days[track_day]+=1

        return{
            'days':days,
            'tracks_by_days':tracks_by_days,
            'time_slots':global_time_slots_by_day,
            'locations':locations
        }

    def_event_agenda_get_tracks(self,event):
        tracks_sudo=event.sudo().track_ids.filtered(lambdatrack:track.date)
        ifnotrequest.env.user.has_group('event.group_event_manager'):
            tracks_sudo=tracks_sudo.filtered(lambdatrack:track.is_publishedortrack.stage_id.is_accepted)
        returntracks_sudo

    def_get_locale_time(self,dt_time,lang_code):
        """Getlocaletimefromdatetimeobject

            :paramdt_time:datetimeobject
            :paramlang_code:languagecode(eg.en_US)
        """
        locale=babel_locale_parse(lang_code)
        returnbabel.dates.format_time(dt_time,format='short',locale=locale)

    deftime_slot_rounder(self,time,rounded_minutes):
        """Roundstonearesthourbyaddingatimedeltahourifminute>=rounded_minutes
            E.g.:Ifrounded_minutes=15->09:26:00becomes09:30:00
                                              09:17:00becomes09:15:00
        """
        return(time.replace(second=0,microsecond=0,minute=0,hour=time.hour)
                +timedelta(minutes=rounded_minutes*(time.minute//rounded_minutes)))

    def_split_track_by_days(self,track,local_tz):
        """
        Basedonthetrackstart_dateandtheduration,
        splitthetrackdurationinto:
            start_timebyday:numberoftimeslot(15minutes)thatthetracktakesonthatday.
        E.g.: startdate=01-01-200010:00PMandduration=3hours
                return{
                    01-01-200010:00:00PM:8(2*4),
                    01-02-200000:00:00AM:4(1*4)
                }
        Alsoreturnasetofallthetimeslots
        """
        start_date=fields.Datetime.from_string(track.date).replace(tzinfo=pytz.utc).astimezone(local_tz)
        start_datetime=self.time_slot_rounder(start_date,15)
        end_datetime=self.time_slot_rounder(start_datetime+timedelta(hours=(track.durationor0.25)),15)
        time_slots_count=int(((end_datetime-start_datetime).total_seconds()/3600)*4)

        time_slots_by_day_start_time={start_datetime:0}
        foriinrange(0,time_slots_count):
            #Ifthenewtimeslotisstillonthecurrentday
            next_day=(start_datetime+timedelta(days=1)).date()
            if(start_datetime+timedelta(minutes=15*i)).date()<=next_day:
                time_slots_by_day_start_time[start_datetime]+=1
            else:
                start_datetime=next_day.datetime()
                time_slots_by_day_start_time[start_datetime]=0

        returntime_slots_by_day_start_time

    def_get_occupied_cells(self,track,rowspan,locations,local_tz):
        """
        Inordertouseonlyoncethecellsthatthetrackswilloccupy,weneedtoreservethosecells
        (time_slot,location)coordinate.Thosecoordinatedwillbegiventothetemplatetoavoidadding
        blankcellswherealreadyoccupiedbyatrack.
        """
        occupied_cells=[]

        start_date=fields.Datetime.from_string(track.date).replace(tzinfo=pytz.utc).astimezone(local_tz)
        start_date=self.time_slot_rounder(start_date,15)
        foriinrange(0,rowspan):
            time_slot=start_date+timedelta(minutes=15*i)
            iftrack.location_id:
                occupied_cells.append((time_slot,track.location_id))
            #whennolocation,reservealllocations
            else:
                occupied_cells+=[(time_slot,location)forlocationinlocationsiflocation]

        returnoccupied_cells

    #------------------------------------------------------------
    #TRACKPAGEVIEW
    #------------------------------------------------------------

    @http.route('''/event/<model("event.event","[('website_track','=',True)]"):event>/track/<model("event.track","[('event_id','=',event.id)]"):track>''',
                type='http',auth="public",website=True,sitemap=True)
    defevent_track_page(self,event,track,**options):
        track=self._fetch_track(track.id,allow_is_accepted=False)

        returnrequest.render(
            "website_event_track.event_track_main",
            self._event_track_page_get_values(event,track.sudo(),**options)
        )

    def_event_track_page_get_values(self,event,track,**options):
        track=track.sudo()

        option_widescreen=options.get('widescreen',False)
        option_widescreen=bool(option_widescreen)ifoption_widescreen!='0'elseFalse
        #searchfortrackslist
        tracks_other=track._get_track_suggestions(
            restrict_domain=self._get_event_tracks_base_domain(track.event_id),
            limit=10
        )

        return{
            #eventinformation
            'event':event,
            'main_object':track,
            'track':track,
            #sidebar
            'tracks_other':tracks_other,
            #options
            'option_widescreen':option_widescreen,
            #environment
            'is_html_empty':is_html_empty,
            'hostname':request.httprequest.host.split(':')[0],
            'user_event_manager':request.env.user.has_group('event.group_event_manager'),
        }

    @http.route("/event/track/toggle_reminder",type="json",auth="public",website=True)
    deftrack_reminder_toggle(self,track_id,set_reminder_on):
        """Setareminderatrackforcurrentvisitor.Trackvisitoriscreatedorupdated
        ifitalreadyexists.Exceptionmadeifun-wishlistingandnotrack_visitor
        recordfound(shouldnothappenunlessmanuallydone).

        :parambooleanset_reminder_on:
          IfTrue,setasawishlist,otherwiseun-wishlisttrack;
          IfthetrackisaKeyTrack(wishlisted_by_default):
            ifset_reminder_on=False,blacklistthetrack_partner
            otherwise,un-blacklistthetrack_partner
        """
        track=self._fetch_track(track_id,allow_is_accepted=True)
        force_create=set_reminder_onortrack.wishlisted_by_default
        event_track_partner=track._get_event_track_visitors(force_create=force_create)
        visitor_sudo=event_track_partner.visitor_id

        ifnottrack.wishlisted_by_default:
            ifnotevent_track_partnerorevent_track_partner.is_wishlisted==set_reminder_on: #ignoreifnewstate=oldstate
                return{'error':'ignored'}
            event_track_partner.is_wishlisted=set_reminder_on
        else:
            ifnotevent_track_partnerorevent_track_partner.is_blacklisted!=set_reminder_on: #ignoreifnewstate=oldstate
                return{'error':'ignored'}
            event_track_partner.is_blacklisted=notset_reminder_on

        result={'reminderOn':set_reminder_on}
        ifrequest.httprequest.cookies.get('visitor_uuid','')!=visitor_sudo.access_token:
            result['visitor_uuid']=visitor_sudo.access_token

        returnresult

    #------------------------------------------------------------
    #TRACKPROPOSAL
    #------------------------------------------------------------

    @http.route(['''/event/<model("event.event"):event>/track_proposal'''],type='http',auth="public",website=True,sitemap=False)
    defevent_track_proposal(self,event,**post):
        ifnotevent.can_access_from_current_website():
            raiseNotFound()

        returnrequest.render("website_event_track.event_track_proposal",{'event':event,'main_object':event})

    @http.route(['''/event/<model("event.event"):event>/track_proposal/post'''],type='http',auth="public",methods=['POST'],website=True)
    defevent_track_proposal_post(self,event,**post):
        ifnotevent.can_access_from_current_website():
            raiseNotFound()

        tags=[]
        fortaginevent.allowed_track_tag_ids:
            ifpost.get('tag_'+str(tag.id)):
                tags.append(tag.id)

        track=request.env['event.track'].sudo().create({
            'name':post['track_name'],
            'partner_name':post['partner_name'],
            'partner_email':post['email_from'],
            'partner_phone':post['phone'],
            'partner_biography':plaintext2html(post['biography']),
            'event_id':event.id,
            'tag_ids':[(6,0,tags)],
            'user_id':False,
            'description':plaintext2html(post['description']),
            'image':base64.b64encode(post['image'].read())ifpost.get('image')elseFalse
        })
        ifrequest.env.user!=request.website.user_id:
            track.sudo().message_subscribe(partner_ids=request.env.user.partner_id.ids)
        else:
            partner=request.env['res.partner'].sudo().search([('email','=',post['email_from'])])
            ifpartner:
                track.sudo().message_subscribe(partner_ids=partner.ids)
        returnrequest.render("website_event_track.event_track_proposal",{'track':track,'event':event})

    #------------------------------------------------------------
    #TOOLS
    #------------------------------------------------------------

    def_fetch_track(self,track_id,allow_is_accepted=False):
        track=request.env['event.track'].browse(track_id).exists()
        ifnottrack:
            raiseNotFound()
        try:
            track.check_access_rights('read')
            track.check_access_rule('read')
        exceptexceptions.AccessError:
            track_sudo=track.sudo()
            ifallow_is_acceptedandtrack_sudo.is_accepted:
                track=track_sudo
            else:
                raiseForbidden()

        event=track.event_id
        #JSONRPChavenowebsiteinrequests
        ifhasattr(request,'website_id')andnotevent.can_access_from_current_website():
            raiseNotFound()
        try:
            event.check_access_rights('read')
            event.check_access_rule('read')
        exceptexceptions.AccessError:
            raiseForbidden()

        returntrack

    def_get_search_tags(self,tag_search):
        #TDEFIXME:makemegeneric(slides,event,...)
        try:
            tag_ids=literal_eval(tag_search)
        exceptException:
            tags=request.env['event.track.tag'].sudo()
        else:
            #performasearchtofilteronexisting/validtagsimplicitly
            tags=request.env['event.track.tag'].sudo().search([('id','in',tag_ids)])
        returntags

    def_get_dt_in_event_tz(self,datetimes,event):
        tz_name=event.date_tz
        return[
            utc.localize(dt,is_dst=False).astimezone(timezone(tz_name))
            fordtindatetimes
        ]
