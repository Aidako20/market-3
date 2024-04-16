#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
fromwerkzeug.exceptionsimportForbidden,NotFound
fromwerkzeug.utilsimportredirect

fromflectraimportexceptions,http
fromflectra.httpimportrequest
fromflectra.addons.http_routing.models.ir_httpimportslug
fromflectra.addons.website_event.controllers.communityimportEventCommunityController
fromflectra.osvimportexpression

_logger=logging.getLogger(__name__)


classWebsiteEventMeetController(EventCommunityController):

    def_get_event_rooms_base_domain(self,event):
        search_domain_base=[('event_id','=',event.id),('is_published','=',True)]
        returnsearch_domain_base

    def_sort_event_rooms(self,room):
        return(room.is_pinned,room.room_last_activity,room.id)

    #------------------------------------------------------------
    #MAINPAGE
    #------------------------------------------------------------

    @http.route(["/event/<model('event.event'):event>/community"],type="http",
                auth="public",website=True,sitemap=True)
    defcommunity(self,event,page=1,lang=None,**kwargs):
        """Displaythemeetingroomsoftheeventonthefrontendside.

        :paramevent:eventforwhichwedisplaythemeetingrooms
        :paramlang:langidusedtoperformasearch
        """
        ifnotevent.can_access_from_current_website():
            raiseForbidden()

        returnrequest.render(
            "website_event_meet.event_meet",
            self._event_meeting_rooms_get_values(event,lang=lang)
        )

    def_event_meeting_rooms_get_values(self,event,lang=None):
        search_domain=self._get_event_rooms_base_domain(event)
        meeting_rooms_all=request.env['event.meeting.room'].sudo().search(search_domain)
        iflang:
            search_domain=expression.AND([
                search_domain,
                [('room_lang_id','=',int(lang))]
            ])
        meeting_rooms=request.env['event.meeting.room'].sudo().search(search_domain)
        meeting_rooms=meeting_rooms.sorted(self._sort_event_rooms,reverse=True)

        is_event_manager=request.env.user.has_group("event.group_event_manager")
        ifnotis_event_manager:
            meeting_rooms=meeting_rooms.filtered(lambdam:notm.room_is_full)

        visitor=request.env['website.visitor']._get_visitor_from_request()

        return{
            #eventinformation
            "event":event.sudo(),
            'main_object':event,
            #rooms
            "meeting_rooms":meeting_rooms,
            "current_lang":request.env["res.lang"].browse(int(lang))iflangelseFalse,
            "available_languages":meeting_rooms_all.mapped("room_lang_id"),
            "default_lang_code":request.context.get('lang',request.env.user.lang),
            "default_username":visitor.display_nameifvisitorelseNone,
            #environment
            "is_event_manager":is_event_manager,
        }

    @http.route("/event/<model('event.event'):event>/meeting_room_create",
                type="http",auth="public",methods=["POST"],website=True)
    defcreate_meeting_room(self,event,**post):
        ifnoteventornotevent.can_access_from_current_website()or(notevent.is_publishedandnotrequest.env.user.user_has_groups('base.group_user'))ornotevent.meeting_room_allow_creation:
            raiseForbidden()

        name=post.get("name")
        summary=post.get("summary")
        target_audience=post.get("audience")
        lang_code=post.get("lang_code")
        max_capacity=post.get("capacity")

        #gettherecordtobesuretheyreallyexist
        lang=request.env["res.lang"].search([("code","=",lang_code)],limit=1)

        ifnotlangormax_capacity=="no_limit":
            raiseForbidden()

        meeting_room=request.env["event.meeting.room"].sudo().create({
            "name":name,
            "summary":summary,
            "target_audience":target_audience,
            "is_pinned":False,
            "event_id":event.id,
            "room_lang_id":lang.id,
            "room_max_capacity":max_capacity,
            "is_published":True,
        })
        _logger.info("Newmeetingroom(%s)createdby%s(uid%s)"%(name,request.httprequest.remote_addr,request.env.uid))

        returnredirect(f"/event/{slug(event)}/meeting_room/{slug(meeting_room)}")

    @http.route(["/event/active_langs"],type="json",auth="public")
    defactive_langs(self):
        returnrequest.env["res.lang"].sudo().get_installed()

    #------------------------------------------------------------
    #ROOMPAGEVIEW
    #------------------------------------------------------------

    @http.route('''/event/<model('event.event',"[('community_menu','=',True)]"):event>/meeting_room/<model("event.meeting.room","[('event_id','=',event.id)]"):meeting_room>''',
                type="http",auth="public",website=True,sitemap=True)
    defevent_meeting_room_page(self,event,meeting_room,**post):
        """Displaythemeetingroomfrontendview.

        :paramevent:Eventforwhichwedisplaythemeetingrooms
        :parammeeting_room:MeetingRoomtodisplay
        """
        ifnotevent.can_access_from_current_website()ormeeting_roomnotinevent.sudo().meeting_room_ids:
            raiseNotFound()

        try:
            meeting_room.check_access_rule('read')
        exceptexceptions.AccessError:
            raiseForbidden()

        meeting_room=meeting_room.sudo()

        returnrequest.render(
            "website_event_meet.event_meet_main",
            self._event_meeting_room_page_get_values(event,meeting_room),
        )

    def_event_meeting_room_page_get_values(self,event,meeting_room):
        #searchformeetingroomlist
        meeting_rooms_other=request.env['event.meeting.room'].sudo().search([
            ('event_id','=',event.id),('id','!=',meeting_room.id),('is_published','=',True),
        ])

        ifnotrequest.env.user.has_group("event.group_event_manager"):
            #onlytheeventmanagercanseemeetingroomswhicharefull
            meeting_rooms_other=meeting_rooms_other.filtered(lambdam:notm.room_is_full)

        meeting_rooms_other=meeting_rooms_other.sorted(self._sort_event_rooms,reverse=True)

        return{
            #eventinformation
            'event':event,
            'main_object':meeting_room,
            'meeting_room':meeting_room,
            #sidebar
            'meeting_rooms_other':meeting_rooms_other,
            #options
            'option_widescreen':True,
            'is_event_manager':request.env.user.has_group('event.group_event_manager'),
        }
