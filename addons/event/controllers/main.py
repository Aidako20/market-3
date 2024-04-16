#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromwerkzeug.exceptionsimportNotFound

fromflectra.httpimportController,request,route,content_disposition


classEventController(Controller):

    @route(['''/event/<model("event.event"):event>/ics'''],type='http',auth="public")
    defevent_ics_file(self,event,**kwargs):
        ifrequest.env.user._is_public():
            frontend_lang=request.httprequest.cookies.get('frontend_lang')
            iffrontend_lang:
                event=event.with_context(lang=frontend_lang)
        files=event._get_ics_file()
        ifnotevent.idinfiles:
            returnNotFound()
        content=files[event.id]
        returnrequest.make_response(content,[
            ('Content-Type','application/octet-stream'),
            ('Content-Length',len(content)),
            ('Content-Disposition',content_disposition('%s.ics'%event.name))
        ])
