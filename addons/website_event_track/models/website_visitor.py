#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classWebsiteVisitor(models.Model):
    _name='website.visitor'
    _inherit=['website.visitor']

    event_track_visitor_ids=fields.One2many(
        'event.track.visitor','visitor_id',string="TrackVisitors",
        groups='event.group_event_user')
    event_track_wishlisted_ids=fields.Many2many(
        'event.track',string="WishlistedTracks",
        compute="_compute_event_track_wishlisted_ids",compute_sudo=True,
        search="_search_event_track_wishlisted_ids",
        groups="event.group_event_user")
    event_track_wishlisted_count=fields.Integer(
        string="#Wishlisted",
        compute="_compute_event_track_wishlisted_ids",compute_sudo=True,
        groups='event.group_event_user')

    @api.depends('parent_id','event_track_visitor_ids.track_id','event_track_visitor_ids.is_wishlisted')
    def_compute_event_track_wishlisted_ids(self):
        #includeparent'strackvisitorsinavisitoro2mfield.Wedon'tadd
        #childoneaschildshouldnothavetrackvisitors(movedtotheparent)
        all_visitors=self+self.parent_id
        results=self.env['event.track.visitor'].read_group(
            [('visitor_id','in',all_visitors.ids),('is_wishlisted','=',True)],
            ['visitor_id','track_id:array_agg'],
            ['visitor_id']
        )
        track_ids_map={result['visitor_id'][0]:result['track_id']forresultinresults}
        forvisitorinself:
            visitor_track_ids=track_ids_map.get(visitor.id,[])
            parent_track_ids=track_ids_map.get(visitor.parent_id.id,[])
            visitor.event_track_wishlisted_ids=visitor_track_ids+[track_idfortrack_idinparent_track_idsiftrack_idnotinvisitor_track_ids]
            visitor.event_track_wishlisted_count=len(visitor.event_track_wishlisted_ids)

    def_search_event_track_wishlisted_ids(self,operator,operand):
        """Searchvisitorswithtermsonwishlistedtracks.E.g.[('event_track_wishlisted_ids',
        'in',[1,2])]shouldreturnvisitorshavingwishlistedtracks1,2as
        wellastheirchildrenfornotificationpurpose."""
        ifoperator=="notin":
            raiseNotImplementedError("Unsupported'NotIn'operationontrackwishlistvisitors")

        track_visitors=self.env['event.track.visitor'].sudo().search([
            ('track_id',operator,operand),
            ('is_wishlisted','=',True)
        ])
        iftrack_visitors:
            visitors=track_visitors.visitor_id
            #searchchildren,evenarchivedone,tocontactthem
            children=self.env['website.visitor'].with_context(
                active_test=False
            ).sudo().search([('parent_id','in',visitors.ids)])
            visitor_ids=(visitors+children).ids
        else:
            visitor_ids=[]

        return[('id','in',visitor_ids)]

    def_link_to_partner(self,partner,update_values=None):
        """Propagatepartnerupdatetotrack_visitorrecords"""
        ifpartner:
            track_visitor_wo_partner=self.event_track_visitor_ids.filtered(lambdatrack_visitor:nottrack_visitor.partner_id)
            iftrack_visitor_wo_partner:
                track_visitor_wo_partner.partner_id=partner
        super(WebsiteVisitor,self)._link_to_partner(partner,update_values=update_values)

    def_link_to_visitor(self,target,keep_unique=True):
        """Overridelinkingprocesstolinkwishlisttothefinalvisitor."""
        self.event_track_visitor_ids.visitor_id=target.id
        returnsuper(WebsiteVisitor,self)._link_to_visitor(target,keep_unique=keep_unique)
