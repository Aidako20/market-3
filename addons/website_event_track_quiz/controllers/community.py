#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importmath

fromflectraimporthttp
fromflectra.addons.http_routing.models.ir_httpimportslug
fromflectra.addons.website_event.controllers.communityimportEventCommunityController
fromflectra.httpimportrequest


classWebsiteEventTrackQuizCommunityController(EventCommunityController):

    _visitors_per_page=30
    _pager_max_pages=5

    @http.route(['/event/<model("event.event"):event>/community/leaderboard/results',
                 '/event/<model("event.event"):event>/community/leaderboard/results/page/<int:page>'],
                type='http',auth="public",website=True,sitemap=False)
    defleaderboard(self,event,page=1,lang=None,**kwargs):
        values=self._get_community_leaderboard_render_values(event,kwargs.get('search'),page)
        returnrequest.render('website_event_track_quiz.event_leaderboard',values)

    @http.route('/event/<model("event.event"):event>/community/leaderboard',
                type='http',auth="public",website=True,sitemap=False)
    defcommunity_leaderboard(self,event,**kwargs):
        values=self._get_community_leaderboard_render_values(event,None,None)
        returnrequest.render('website_event_track_quiz.event_leaderboard',values)

    @http.route('/event/<model("event.event"):event>/community',
                type='http',auth="public",website=True,sitemap=False)
    defcommunity(self,event,**kwargs):
        values=self._get_community_leaderboard_render_values(event,None,None)
        returnrequest.render('website_event_track_quiz.event_leaderboard',values)

    def_get_community_leaderboard_render_values(self,event,search_term,page):
        values=self._get_leaderboard(event,search_term)
        values.update({'event':event,'search':search_term})

        user_count=len(values['visitors'])
        ifuser_count:
            page_count=math.ceil(user_count/self._visitors_per_page)
            url='/event/%s/community/leaderboard/results'%(slug(event))
            ifvalues.get('current_visitor_position')andnotpage:
                values['scroll_to_position']=True
                page=math.ceil(values['current_visitor_position']/self._visitors_per_page)
            elifnotpage:
                page=1
            pager=request.website.pager(url=url,total=user_count,page=page,step=self._visitors_per_page,
                                          scope=page_countifpage_count<self._pager_max_pageselseself._pager_max_pages,
                                          url_args={'search':search_term})
            values['visitors']=values['visitors'][(page-1)*self._visitors_per_page:(page)*self._visitors_per_page]
        else:
            pager={'page_count':0}
        values.update({'pager':pager})
        returnvalues

    def_get_leaderboard(self,event,searched_name=None):
        current_visitor=request.env['website.visitor']._get_visitor_from_request(force_create=False)
        track_visitor_data=request.env['event.track.visitor'].sudo().read_group(
            [('track_id','in',event.track_ids.ids),
             ('visitor_id','!=',False),
             ('quiz_points','>',0)],
            ['id','visitor_id','points:sum(quiz_points)'],
            ['visitor_id'],orderby="pointsDESC")
        data_map={datum['visitor_id'][0]:datum['points']fordatumintrack_visitor_dataifdatum.get('visitor_id')}
        leaderboard=[]
        position=1
        current_visitor_position=False
        visitors_by_id={
            visitor.id:visitor
            forvisitorinrequest.env['website.visitor'].sudo().browse(data_map.keys())
        }
        forvisitor_id,pointsindata_map.items():
            visitor=visitors_by_id.get(visitor_id)
            ifnotvisitor:
                continue
            if(searched_nameandsearched_name.lower()invisitor.display_name.lower())ornotsearched_name:
                leaderboard.append({'visitor':visitor,'points':points,'position':position})
                ifcurrent_visitorandcurrent_visitor==visitor:
                    current_visitor_position=position
            position=position+1

        return{
            'top3_visitors':leaderboard[:3],
            'visitors':leaderboard,
            'current_visitor_position':current_visitor_position,
            'current_visitor':current_visitor,
            'searched_name':searched_name
        }
