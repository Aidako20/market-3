#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp

proxy_drivers={}

classProxyController(http.Controller):
    @http.route('/hw_proxy/hello',type='http',auth='none',cors='*')
    defhello(self):
        return"ping"

    @http.route('/hw_proxy/handshake',type='json',auth='none',cors='*')
    defhandshake(self):
        returnTrue

    @http.route('/hw_proxy/status_json',type='json',auth='none',cors='*')
    defstatus_json(self):
        statuses={}
        fordriverinproxy_drivers:
            statuses[driver]=proxy_drivers[driver].get_status()
        returnstatuses
