#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp


classIoTBoxHttpRequest(http.HttpRequest):
    defdispatch(self):
        ifself._is_cors_preflight(http.request.endpoint):
            #UsingthePoSindebugmodeinv12,thecallto'/hw_proxy/handshake'containsthe
            #'X-Debug-Mode'header,whichwasremovedfrom'Access-Control-Allow-Headers'inv13.
            #Whenthecodeofhttp.pyisnotcheckedouttov12(i.e.inCommunity),theconnection
            #failsastheheaderisrejectedandnoneofthedevicescanbeused.
            headers={
                'Access-Control-Max-Age':60*60*24,
                'Access-Control-Allow-Headers':'Origin,X-Requested-With,Content-Type,Accept,Authorization,X-Debug-Mode'
            }
            returnhttp.Response(status=200,headers=headers)
        returnsuper(IoTBoxHttpRequest,self).dispatch()


classIoTBoxRoot(http.Root):
    defsetup_db(self,httprequest):
        #NodatabaseontheIoTBox
        pass

    defget_request(self,httprequest):
        #OverrideHttpRequestwithIoTBoxHttpRequest
        ifhttprequest.mimetypenotin("application/json","application/json-rpc"):
            returnIoTBoxHttpRequest(httprequest)
        returnsuper(IoTBoxRoot,self).get_request(httprequest)

http.Root=IoTBoxRoot
http.root=IoTBoxRoot()
