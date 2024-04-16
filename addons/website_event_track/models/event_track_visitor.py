#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classTrackVisitor(models.Model):
    """Tablelinkingtrackandvisitors."""
    _name='event.track.visitor'
    _description='Track/VisitorLink'
    _table='event_track_visitor'
    _rec_name='track_id'
    _order='track_id'

    partner_id=fields.Many2one(
        'res.partner',string='Partner',compute='_compute_partner_id',
        index=True,ondelete='setnull',readonly=False,store=True)
    visitor_id=fields.Many2one(
        'website.visitor',string='Visitor',index=True,ondelete='cascade')
    track_id=fields.Many2one(
        'event.track',string='Track',
        index=True,required=True,ondelete='cascade')
    is_wishlisted=fields.Boolean(string="IsWishlisted")
    is_blacklisted=fields.Boolean(string="Isreminderoff",help="Askeytrackcannotbeun-wishlisted,thisfieldstorethepartnerchoicetoremovethereminderforkeytracks.")

    @api.depends('visitor_id')
    def_compute_partner_id(self):
        fortrack_visitorinself:
            iftrack_visitor.visitor_id.partner_idandnottrack_visitor.partner_id:
                track_visitor.partner_id=track_visitor.visitor_id.partner_id
            elifnottrack_visitor.partner_id:
                track_visitor.partner_id=False
