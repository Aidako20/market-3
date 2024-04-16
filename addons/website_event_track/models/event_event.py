#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.addons.http_routing.models.ir_httpimportslug


classEvent(models.Model):
    _inherit="event.event"

    track_ids=fields.One2many('event.track','event_id','Tracks')
    track_count=fields.Integer('TrackCount',compute='_compute_track_count')
    sponsor_ids=fields.One2many('event.sponsor','event_id','Sponsors')
    sponsor_count=fields.Integer('SponsorCount',compute='_compute_sponsor_count')
    website_track=fields.Boolean(
        'TracksonWebsite',compute='_compute_website_track',
        readonly=False,store=True)
    website_track_proposal=fields.Boolean(
        'ProposalsonWebsite',compute='_compute_website_track_proposal',
        readonly=False,store=True)
    track_menu_ids=fields.One2many('website.event.menu','event_id',string='EventTracksMenus',domain=[('menu_type','=','track')])
    track_proposal_menu_ids=fields.One2many('website.event.menu','event_id',string='EventProposalsMenus',domain=[('menu_type','=','track_proposal')])
    allowed_track_tag_ids=fields.Many2many('event.track.tag',relation='event_allowed_track_tags_rel',string='AvailableTrackTags')
    tracks_tag_ids=fields.Many2many(
        'event.track.tag',relation='event_track_tags_rel',string='TrackTags',
        compute='_compute_tracks_tag_ids',store=True)

    def_compute_track_count(self):
        data=self.env['event.track'].read_group([('stage_id.is_cancel','!=',True)],['event_id'],['event_id'])
        result=dict((data['event_id'][0],data['event_id_count'])fordataindata)
        foreventinself:
            event.track_count=result.get(event.id,0)

    def_compute_sponsor_count(self):
        data=self.env['event.sponsor'].read_group([],['event_id'],['event_id'])
        result=dict((data['event_id'][0],data['event_id_count'])fordataindata)
        foreventinself:
            event.sponsor_count=result.get(event.id,0)

    @api.depends('event_type_id','website_menu')
    def_compute_website_track(self):
        """Propagateevent_typeconfiguration(onlyatchange);otherwisepropagate
        website_menuupdatedvalue.AlsoforceTrueistrack_proposalchanges."""
        foreventinself:
            ifevent.event_type_idandevent.event_type_id!=event._origin.event_type_id:
                event.website_track=event.event_type_id.website_track
            elifevent.website_menuand(event.website_menu!=event._origin.website_menuornotevent.website_track):
                event.website_track=True
            elifnotevent.website_menu:
                event.website_track=False

    @api.depends('event_type_id','website_track')
    def_compute_website_track_proposal(self):
        """Propagateevent_typeconfiguration(onlyatchange);otherwisepropagate
        website_trackupdatedvalue(bothtogetherTrueorFalseatupdate)."""
        foreventinself:
            ifevent.event_type_idandevent.event_type_id!=event._origin.event_type_id:
                event.website_track_proposal=event.event_type_id.website_track_proposal
            elifevent.website_track!=event._origin.website_trackornotevent.website_trackornotevent.website_track_proposal:
                event.website_track_proposal=event.website_track

    @api.depends('track_ids.tag_ids','track_ids.tag_ids.color')
    def_compute_tracks_tag_ids(self):
        foreventinself:
            event.tracks_tag_ids=event.track_ids.mapped('tag_ids').filtered(lambdatag:tag.color!=0).ids

    #------------------------------------------------------------
    #WEBSITEMENUMANAGEMENT
    #------------------------------------------------------------

    deftoggle_website_track(self,val):
        self.website_track=val

    deftoggle_website_track_proposal(self,val):
        self.website_track_proposal=val

    def_get_menu_update_fields(self):
        returnsuper(Event,self)._get_menu_update_fields()+['website_track','website_track_proposal']

    def_update_website_menus(self,menus_update_by_field=None):
        super(Event,self)._update_website_menus(menus_update_by_field=menus_update_by_field)
        foreventinself:
            ifevent.menu_idand(notmenus_update_by_fieldoreventinmenus_update_by_field.get('website_track')):
                event._update_website_menu_entry('website_track','track_menu_ids','_get_track_menu_entries')
            ifevent.menu_idand(notmenus_update_by_fieldoreventinmenus_update_by_field.get('website_track_proposal')):
                event._update_website_menu_entry('website_track_proposal','track_proposal_menu_ids','_get_track_proposal_menu_entries')

    def_get_menu_type_field_matching(self):
        res=super(Event,self)._get_menu_type_field_matching()
        res['track_proposal']='website_track_proposal'
        returnres

    def_get_track_menu_entries(self):
        """Methodreturningmenuentriestodisplayonthewebsiteviewofthe
        event,possiblydependingonsomeoptionsininheritingmodules.

        Eachmenuentryisatuplecontaining:
          *name:menuitemname
          *url:ifset,urltoaroute(donotusexml_idinthatcase);
          *xml_id:templatelinkedtothepage(donotuseurlinthatcase);
          *menu_type:keylinkedtothemenu,usedtocategorizethecreated
            website.event.menu;
        """
        self.ensure_one()
        return[
            (_('Talks'),'/event/%s/track'%slug(self),False,10,'track'),
            (_('Agenda'),'/event/%s/agenda'%slug(self),False,70,'track')
        ]

    def_get_track_proposal_menu_entries(self):
        """Seewebsite_event_track._get_track_menu_entries()"""
        self.ensure_one()
        return[(_('TalkProposals'),'/event/%s/track_proposal'%slug(self),False,15,'track_proposal')]
