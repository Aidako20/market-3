#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.addons.http_routing.models.ir_httpimportslug


classEventEvent(models.Model):
    _inherit="event.event"

    exhibitor_menu=fields.Boolean(
        string='ShowcaseExhibitors',compute='_compute_exhibitor_menu',
        readonly=False,store=True)
    exhibitor_menu_ids=fields.One2many(
        'website.event.menu','event_id',string='ExhibitorsMenus',
        domain=[('menu_type','=','exhibitor')])

    @api.depends('event_type_id','website_menu','exhibitor_menu')
    def_compute_exhibitor_menu(self):
        foreventinself:
            ifevent.event_type_idandevent.event_type_id!=event._origin.event_type_id:
                event.exhibitor_menu=event.event_type_id.exhibitor_menu
            elifevent.website_menuand(event.website_menu!=event._origin.website_menuornotevent.exhibitor_menu):
                event.exhibitor_menu=True
            elifnotevent.website_menu:
                event.exhibitor_menu=False

    #------------------------------------------------------------
    #WEBSITEMENUMANAGEMENT
    #------------------------------------------------------------

    deftoggle_exhibitor_menu(self,val):
        self.exhibitor_menu=val

    def_get_menu_update_fields(self):
        returnsuper(EventEvent,self)._get_menu_update_fields()+['exhibitor_menu']

    def_update_website_menus(self,menus_update_by_field=None):
        super(EventEvent,self)._update_website_menus(menus_update_by_field=menus_update_by_field)
        foreventinself:
            ifevent.menu_idand(notmenus_update_by_fieldoreventinmenus_update_by_field.get('exhibitor_menu')):
                event._update_website_menu_entry('exhibitor_menu','exhibitor_menu_ids','_get_exhibitor_menu_entries')

    def_get_menu_type_field_matching(self):
        res=super(EventEvent,self)._get_menu_type_field_matching()
        res['exhibitor']='exhibitor_menu'
        returnres

    def_get_exhibitor_menu_entries(self):
        self.ensure_one()
        return[(_('Exhibitors'),'/event/%s/exhibitors'%slug(self),False,60,'exhibitor')]
