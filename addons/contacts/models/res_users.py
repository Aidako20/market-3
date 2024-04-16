#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,modules


classUsers(models.Model):
    _name='res.users'
    _inherit=['res.users']

    @api.model
    defsystray_get_activities(self):
        """Updatethesystrayiconofres.partneractivitiestousethe
        contactapplicationoneinsteadofbaseicon."""
        activities=super(Users,self).systray_get_activities()
        foractivityinactivities:
            ifactivity['model']!='res.partner':
                continue
            activity['icon']=modules.module.get_module_icon('contacts')
        returnactivities
