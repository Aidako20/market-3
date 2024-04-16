#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp
fromflectra.httpimportrequest


classHrAttendance(http.Controller):
    @http.route('/hr_attendance/kiosk_keepalive',auth='user',type='json')
    defkiosk_keepalive(self):
        request.httprequest.session.modified=True
        return{}
