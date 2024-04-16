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
            #specificallycheckfor/trackinmenuURL;toavoiduncheckingtrackfieldwhenremoving
            #agendapagethathasalsomenu_type='track'
            ifevent_menu.menu_type=='track'and'/track'inevent_menu.menu_id.url:
                to_update.append('website_track')

        #callsuperthatresumestheunlinkofmenusentries(includingwebsiteeventmenus)
        res=super(WebsiteMenu,self).unlink()

        #updateevents
        forevent,to_updateinevent_updates.items():
            ifto_update:
                event.write(dict((fname,False)forfnameinto_update))

        returnres
