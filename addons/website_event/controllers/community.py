#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp
fromflectra.httpimportrequest


classEventCommunityController(http.Controller):

    @http.route('/event/<model("event.event"):event>/community',type="http",auth="public",website=True,sitemap=False)
    defcommunity(self,event,lang=None,**kwargs):
        """Thisskeletonroutewillbeoverrideninwebsite_event_track_quiz,website_event_meetandwebsite_event_meet_quiz."""
        returnrequest.render('website.page_404')
