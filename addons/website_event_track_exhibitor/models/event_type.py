#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classEventType(models.Model):
    _inherit="event.type"

    exhibitor_menu=fields.Boolean(
        string='ShowcaseExhibitors',compute='_compute_exhibitor_menu',
        readonly=False,store=True,
        help='Displayexhibitorsonwebsite')

    @api.depends('website_menu')
    def_compute_exhibitor_menu(self):
        forevent_typeinself:
            event_type.exhibitor_menu=event_type.website_menu
