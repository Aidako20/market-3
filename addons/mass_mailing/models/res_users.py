#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,_


classUsers(models.Model):
    _name='res.users'
    _inherit=['res.users']

    @api.model
    defsystray_get_activities(self):
        """Updatesystraynameofmailing.mailingfrom"MassMailing"
            to"EmailMarketing".
        """
        activities=super(Users,self).systray_get_activities()
        foractivityinactivities:
            ifactivity.get('model')=='mailing.mailing':
                activity['name']=_('EmailMarketing')
                break
        returnactivities
