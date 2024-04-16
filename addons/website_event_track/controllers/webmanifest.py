#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson
importpytz

fromflectraimporthttp
fromflectra.addons.http_routing.models.ir_httpimporturl_for
fromflectra.httpimportrequest
fromflectra.modules.moduleimportget_module_resource
fromflectra.toolsimportustr
fromflectra.tools.translateimport_


classTrackManifest(http.Controller):

    @http.route('/event/manifest.webmanifest',type='http',auth='public',methods=['GET'],website=True,sitemap=False)
    defwebmanifest(self):
        """ReturnsaWebManifestdescribingthemetadataassociatedwithawebapplication.
        Usingthismetadata,useragentscanprovidedeveloperswithmeanstocreateuser
        experiencesthataremorecomparabletothatofanativeapplication.
        """
        website=request.website
        manifest={
            'name':website.events_app_name,
            'short_name':website.events_app_name,
            'description':_('%sOnlineEventsApplication')%website.company_id.name,
            'scope':url_for('/event'),
            'start_url':url_for('/event'),
            'display':'standalone',
            'background_color':'#ffffff',
            'theme_color':'#009EFB',
        }
        icon_sizes=['192x192','512x512']
        manifest['icons']=[{
            'src':website.image_url(website,'app_icon',size=size),
            'sizes':size,
            'type':'image/png',
        }forsizeinicon_sizes]
        body=json.dumps(manifest,default=ustr)
        response=request.make_response(body,[
            ('Content-Type','application/manifest+json'),
        ])
        returnresponse

    @http.route('/event/service-worker.js',type='http',auth='public',methods=['GET'],website=True,sitemap=False)
    defservice_worker(self):
        """ReturnsaServiceWorkerjavascriptfilescopedforwebsite_event
        """
        sw_file=get_module_resource('website_event_track','static/src/js/service_worker.js')
        withopen(sw_file,'r')asfp:
            body=fp.read()
        js_cdn_url='undefined'
        ifrequest.website.cdn_activated:
            cdn_url=request.website.cdn_url.replace('"','%22').replace('\x5c','%5C')
            js_cdn_url='"%s"'%cdn_url
        body=body.replace('__FLECTRA_CDN_URL__',js_cdn_url)
        response=request.make_response(body,[
            ('Content-Type','text/javascript'),
            ('Service-Worker-Allowed',url_for('/event')),
        ])
        returnresponse

    @http.route('/event/offline',type='http',auth='public',methods=['GET'],website=True,sitemap=False)
    defoffline(self):
        """Returnstheofflinepageusedbythe'website_event'PWA
        """
        returnrequest.render('website_event_track.pwa_offline')
