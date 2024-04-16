#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,_
fromflectra.addons.http_routing.models.ir_httpimporturl_for


classWebsite(models.Model):
    _inherit="website"

    website_slide_google_app_key=fields.Char('GoogleDocKey',groups='base.group_system')

    defget_suggested_controllers(self):
        suggested_controllers=super(Website,self).get_suggested_controllers()
        suggested_controllers.append((_('Courses'),url_for('/slides'),'website_slides'))
        returnsuggested_controllers
