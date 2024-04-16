#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classEventType(models.Model):
    _name='event.type'
    _inherit=['event.type']

    website_menu=fields.Boolean('DisplayadedicatedmenuonWebsite')
    community_menu=fields.Boolean(
        "CommunityMenu",compute="_compute_community_menu",
        readonly=False,store=True,
        help="Displaycommunitytabonwebsite")
    menu_register_cta=fields.Boolean(
        'AddRegisterButton',compute='_compute_menu_register_cta',
        readonly=False,store=True)

    @api.depends('website_menu')
    def_compute_community_menu(self):
        forevent_typeinself:
            event_type.community_menu=event_type.website_menu

    @api.depends('website_menu')
    def_compute_menu_register_cta(self):
        forevent_typeinself:
            event_type.menu_register_cta=event_type.website_menu
