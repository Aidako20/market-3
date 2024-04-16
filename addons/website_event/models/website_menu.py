#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classWebsiteMenu(models.Model):
    _inherit="website.menu"

    defunlink(self):
        """Overridetosynchronizeeventconfigurationfieldswithmenudeletion.
        Thisshouldbecleanedinupcomingversions."""   
        event_updates={}
        website_event_menus=self.env['website.event.menu'].search([('menu_id','in',self.ids)])
        forevent_menuinwebsite_event_menus:
            to_update=event_updates.setdefault(event_menu.event_id,list())
            formenu_type,fnameinevent_menu.event_id._get_menu_type_field_matching().items():
                ifevent_menu.menu_type==menu_type:
                    to_update.append(fname)

        #callsuperthatresumestheunlinkofmenusentries(includingwebsiteeventmenus)
        res=super(WebsiteMenu,self).unlink()

        #updateevents
        forevent,to_updateinevent_updates.items():
            ifto_update:
                event.write(dict((fname,False)forfnameinto_update))

        returnres
