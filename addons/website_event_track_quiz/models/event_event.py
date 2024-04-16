#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classEvent(models.Model):
    _inherit="event.event"

    @api.depends("event_type_id","website_menu","community_menu")
    def_compute_community_menu(self):
        """Attypeonchange:synchronize.Atwebsite_menuupdate:synchronize."""
        foreventinself:
            ifevent.event_type_idandevent.event_type_id!=event._origin.event_type_id:
                event.community_menu=event.event_type_id.community_menu
            elifevent.website_menuand(event.website_menu!=event._origin.website_menuornotevent.community_menu):
                event.community_menu=True
            elifnotevent.website_menu:
                event.community_menu=False
