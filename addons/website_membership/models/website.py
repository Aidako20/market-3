#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,_
fromflectra.addons.http_routing.models.ir_httpimporturl_for


classWebsite(models.Model):
    _inherit="website"

    defget_suggested_controllers(self):
        suggested_controllers=super(Website,self).get_suggested_controllers()
        suggested_controllers.append((_('Members'),url_for('/members'),'website_membership'))
        returnsuggested_controllers
