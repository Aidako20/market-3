#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimporttimedelta
frompytzimportutc
fromrandomimportrandint

fromflectraimportapi,fields,models,tools
fromflectra.addons.http_routing.models.ir_httpimportslug
fromflectra.osvimportexpression
fromflectra.tools.mailimportis_html_empty
fromflectra.tools.translateimport_,html_translate


classTrack(models.Model):
    _name="event.track"
    _description='EventTrack'
    _order='priority,date'
    _inherit=['mail.thread','mail.activity.mixin','website.seo.metadata','website.published.mixin']

    @api.model
    def_get_default_stage_id(self):
        returnself.env['event.track.stage'].search([],limit=1).id

    #description
    name=fields.Char('Title',required=True,translate=True)
    event_id=fields.Many2one('event.event','Event',required=True)
    active=fields.Boolean(default=True)
    user_id=fields.Many2one('res.users','Responsible',tracking=True,default=lambdaself:self.env.user)
    company_id=fields.Many2one('res.company',related='event_id.company_id')
    tag_ids=fields.Many2many('event.track.tag',string='Tags')
    description=fields.Html(translate=html_translate,sanitize_attributes=False,sanitize_form=False)
    color=fields.Integer('Color')
    priority=fields.Selection([
        ('0','Low'),('1','Medium'),
        ('2','High'),('3','Highest')],
        'Priority',required=True,default='1')
    #management
    stage_id=fields.Many2one(
        'event.track.stage',string='Stage',ondelete='restrict',
        index=True,copy=False,default=_get_default_stage_id,
        group_expand='_read_group_stage_ids',
        required=True,tracking=True)
    is_accepted=fields.Boolean('IsAccepted',related='stage_id.is_accepted',readonly=True)
    kanban_state=fields.Selection([
        ('normal','Grey'),
        ('done','Green'),
        ('blocked','Red')],string='KanbanState',
        copy=False,default='normal',required=True,tracking=True,
        help="Atrack'skanbanstateindicatesspecialsituationsaffectingit:\n"
             "*Greyisthedefaultsituation\n"
             "*Redindicatessomethingispreventingtheprogressofthistrack\n"
             "*Greenindicatesthetrackisreadytobepulledtothenextstage")
    #speaker
    partner_id=fields.Many2one('res.partner','Speaker')
    partner_name=fields.Char(
        string='Name',compute='_compute_partner_name',
        readonly=False,store=True,tracking=10)
    partner_email=fields.Char(
        string='Email',compute='_compute_partner_email',
        readonly=False,store=True,tracking=20)
    partner_phone=fields.Char(
        string='Phone',compute='_compute_partner_phone',
        readonly=False,store=True,tracking=30)
    partner_biography=fields.Html(
        string='Biography',compute='_compute_partner_biography',
        readonly=False,store=True)
    partner_function=fields.Char(
        'JobPosition',related='partner_id.function',
        compute_sudo=True,readonly=True)
    partner_company_name=fields.Char(
        'CompanyName',related='partner_id.parent_name',
        compute_sudo=True,readonly=True)
    image=fields.Image(
        string="SpeakerPhoto",compute="_compute_speaker_image",
        readonly=False,store=True,
        max_width=256,max_height=256)
    location_id=fields.Many2one('event.track.location','Location')
    #timeinformation
    date=fields.Datetime('TrackDate')
    date_end=fields.Datetime('TrackEndDate',compute='_compute_end_date',store=True)
    duration=fields.Float('Duration',default=1.5,help="Trackdurationinhours.")
    is_track_live=fields.Boolean(
        'IsTrackLive',compute='_compute_track_time_data',
        help="Trackhasstartedandisongoing")
    is_track_soon=fields.Boolean(
        'IsTrackSoon',compute='_compute_track_time_data',
        help="Trackbeginssoon")
    is_track_today=fields.Boolean(
        'IsTrackToday',compute='_compute_track_time_data',
        help="Trackbeginstoday")
    is_track_upcoming=fields.Boolean(
        'IsTrackUpcoming',compute='_compute_track_time_data',
        help="Trackisnotyetstarted")
    is_track_done=fields.Boolean(
        'IsTrackDone',compute='_compute_track_time_data',
        help="Trackisfinished")
    track_start_remaining=fields.Integer(
        'Minutesbeforetrackstarts',compute='_compute_track_time_data',
        help="Remainingtimebeforetrackstarts(seconds)")
    track_start_relative=fields.Integer(
        'Minutescomparetotrackstart',compute='_compute_track_time_data',
        help="Relativetimecomparedtotrackstart(seconds)")
    #frontenddescription
    website_image=fields.Image(string="WebsiteImage",max_width=1024,max_height=1024)
    website_image_url=fields.Char(
        string='ImageURL',compute='_compute_website_image_url',
        compute_sudo=True,store=False)
    #wishlist/visitorsmanagement
    event_track_visitor_ids=fields.One2many(
        'event.track.visitor','track_id',string="TrackVisitors",
        groups="event.group_event_user")
    is_reminder_on=fields.Boolean('IsReminderOn',compute='_compute_is_reminder_on')
    wishlist_visitor_ids=fields.Many2many(
        'website.visitor',string="VisitorWishlist",
        compute="_compute_wishlist_visitor_ids",compute_sudo=True,
        search="_search_wishlist_visitor_ids",
        groups="event.group_event_user")
    wishlist_visitor_count=fields.Integer(
        string="#Wishlisted",
        compute="_compute_wishlist_visitor_ids",compute_sudo=True,
        groups="event.group_event_user")
    wishlisted_by_default=fields.Boolean(
        string='AlwaysWishlisted',
        help="""Ifset,thetalkwillbestarredforeachattendeeregisteredtotheevent.Theattendeewon'tbeabletoun-starthistalk.""")
    #Calltoaction
    website_cta=fields.Boolean('MagicButton')
    website_cta_title=fields.Char('ButtonTitle')
    website_cta_url=fields.Char('ButtonTargetURL')
    website_cta_delay=fields.Integer('Buttonappears')
    #timeinformationforCTA
    is_website_cta_live=fields.Boolean(
        'IsCTALive',compute='_compute_cta_time_data',
        help="CTAbuttonisavailable")
    website_cta_start_remaining=fields.Integer(
        'MinutesbeforeCTAstarts',compute='_compute_cta_time_data',
        help="RemainingtimebeforeCTAstarts(seconds)")

    @api.depends('name')
    def_compute_website_url(self):
        super(Track,self)._compute_website_url()
        fortrackinself:
            iftrack.id:
                track.website_url='/event/%s/track/%s'%(slug(track.event_id),slug(track))

    #SPEAKER

    @api.depends('partner_id')
    def_compute_partner_name(self):
        fortrackinself:
            ifnottrack.partner_nameortrack.partner_id:
                track.partner_name=track.partner_id.name

    @api.depends('partner_id')
    def_compute_partner_email(self):
        fortrackinself:
            ifnottrack.partner_emailortrack.partner_id:
                track.partner_email=track.partner_id.email

    @api.depends('partner_id')
    def_compute_partner_phone(self):
        fortrackinself:
            ifnottrack.partner_phoneortrack.partner_id:
                track.partner_phone=track.partner_id.phone

    @api.depends('partner_id')
    def_compute_partner_biography(self):
        fortrackinself:
            ifnottrack.partner_biography:
                track.partner_biography=track.partner_id.website_description
            eliftrack.partner_idandis_html_empty(track.partner_biography)and\
                notis_html_empty(track.partner_id.website_description):
                track.partner_biography=track.partner_id.website_description

    @api.depends('partner_id')
    def_compute_speaker_image(self):
        fortrackinself:
            ifnottrack.image:
                track.image=track.partner_id.image_256

    #TIME

    @api.depends('date','duration')
    def_compute_end_date(self):
        fortrackinself:
            iftrack.date:
                delta=timedelta(minutes=60*track.duration)
                track.date_end=track.date+delta
            else:
                track.date_end=False


    #FRONTENDDESCRIPTION

    @api.depends('image','partner_id.image_256')
    def_compute_website_image_url(self):
        fortrackinself:
            iftrack.website_image:
                track.website_image_url=self.env['website'].image_url(track,'website_image',size=1024)
            else:
                track.website_image_url='/website_event_track/static/src/img/event_track_default_%d.jpeg'%(track.id%2)

    #WISHLIST/VISITORMANAGEMENT

    @api.depends('wishlisted_by_default','event_track_visitor_ids.visitor_id',
                 'event_track_visitor_ids.partner_id','event_track_visitor_ids.is_wishlisted',
                 'event_track_visitor_ids.is_blacklisted')
    @api.depends_context('uid')
    def_compute_is_reminder_on(self):
        current_visitor=self.env['website.visitor']._get_visitor_from_request(force_create=False)
        ifself.env.user._is_public()andnotcurrent_visitor:
            fortrackinself:
                track.is_reminder_on=track.wishlisted_by_default
        else:
            ifself.env.user._is_public():
                domain=[('visitor_id','=',current_visitor.id)]
            elifcurrent_visitor:
                domain=[
                    '|',
                    ('partner_id','=',self.env.user.partner_id.id),
                    ('visitor_id','=',current_visitor.id)
                ]
            else:
                domain=[('partner_id','=',self.env.user.partner_id.id)]

            event_track_visitors=self.env['event.track.visitor'].sudo().search_read(
                expression.AND([
                    domain,
                    [('track_id','in',self.ids)]
                ]),fields=['track_id','is_wishlisted','is_blacklisted']
            )

            wishlist_map={
                track_visitor['track_id'][0]:{
                    'is_wishlisted':track_visitor['is_wishlisted'],
                    'is_blacklisted':track_visitor['is_blacklisted']
                }fortrack_visitorinevent_track_visitors
            }
            fortrackinself:
                ifwishlist_map.get(track.id):
                    track.is_reminder_on=wishlist_map.get(track.id)['is_wishlisted']or(track.wishlisted_by_defaultandnotwishlist_map[track.id]['is_blacklisted'])
                else:
                    track.is_reminder_on=track.wishlisted_by_default

    @api.depends('event_track_visitor_ids.visitor_id','event_track_visitor_ids.is_wishlisted')
    def_compute_wishlist_visitor_ids(self):
        results=self.env['event.track.visitor'].read_group(
            [('track_id','in',self.ids),('is_wishlisted','=',True)],
            ['track_id','visitor_id:array_agg'],
            ['track_id']
        )
        visitor_ids_map={result['track_id'][0]:result['visitor_id']forresultinresults}
        fortrackinself:
            track.wishlist_visitor_ids=visitor_ids_map.get(track.id,[])
            track.wishlist_visitor_count=len(visitor_ids_map.get(track.id,[]))

    def_search_wishlist_visitor_ids(self,operator,operand):
        ifoperator=="notin":
            raiseNotImplementedError("Unsupported'NotIn'operationontrackwishlistvisitors")

        track_visitors=self.env['event.track.visitor'].sudo().search([
            ('visitor_id',operator,operand),
            ('is_wishlisted','=',True)
        ])
        return[('id','in',track_visitors.track_id.ids)]

    #TIME

    @api.depends('date','date_end')
    def_compute_track_time_data(self):
        """Computestartandremainingtimefortrackitself.Doeverythingin
        UTCaswecomputeonlytimedeltashere."""
        now_utc=utc.localize(fields.Datetime.now().replace(microsecond=0))
        fortrackinself:
            ifnottrack.date:
                track.is_track_live=track.is_track_soon=track.is_track_today=track.is_track_upcoming=track.is_track_done=False
                track.track_start_relative=track.track_start_remaining=0
                continue
            date_begin_utc=utc.localize(track.date,is_dst=False)
            date_end_utc=utc.localize(track.date_end,is_dst=False)
            track.is_track_live=date_begin_utc<=now_utc<date_end_utc
            track.is_track_soon=(date_begin_utc-now_utc).total_seconds()<30*60ifdate_begin_utc>now_utcelseFalse
            track.is_track_today=date_begin_utc.date()==now_utc.date()
            track.is_track_upcoming=date_begin_utc>now_utc
            track.is_track_done=date_end_utc<=now_utc
            ifdate_begin_utc>=now_utc:
                track.track_start_relative=int((date_begin_utc-now_utc).total_seconds())
                track.track_start_remaining=track.track_start_relative
            else:
                track.track_start_relative=int((now_utc-date_begin_utc).total_seconds())
                track.track_start_remaining=0

    @api.depends('date','date_end','website_cta','website_cta_delay')
    def_compute_cta_time_data(self):
        """Computestartandremainingtimefortrackitself.Doeverythingin
        UTCaswecomputeonlytimedeltashere."""
        now_utc=utc.localize(fields.Datetime.now().replace(microsecond=0))
        fortrackinself:
            ifnottrack.website_cta:
                track.is_website_cta_live=track.website_cta_start_remaining=False
                continue

            date_begin_utc=utc.localize(track.date,is_dst=False)+timedelta(minutes=track.website_cta_delayor0)
            date_end_utc=utc.localize(track.date_end,is_dst=False)
            track.is_website_cta_live=date_begin_utc<=now_utc<=date_end_utc
            ifdate_begin_utc>=now_utc:
                td=date_begin_utc-now_utc
                track.website_cta_start_remaining=int(td.total_seconds())
            else:
                track.website_cta_start_remaining=0

    #------------------------------------------------------------
    #CRUD
    #------------------------------------------------------------

    @api.model_create_multi
    defcreate(self,vals_list):
        forvaluesinvals_list:
            ifvalues.get('website_cta_url'):
                values['website_cta_url']=self.env['res.partner']._clean_website(values['website_cta_url'])

        tracks=super(Track,self).create(vals_list)

        fortrackintracks:
            email_values={}ifself.env.user.emailelse{'email_from':self.env.company.catchall_formatted}
            track.event_id.message_post_with_view(
                'website_event_track.event_track_template_new',
                values={'track':track},
                subject=track.name,
                subtype_id=self.env.ref('website_event_track.mt_event_track').id,
                **email_values,
            )
            track._synchronize_with_stage(track.stage_id)

        returntracks

    defwrite(self,vals):
        ifvals.get('website_cta_url'):
            vals['website_cta_url']=self.env['res.partner']._clean_website(vals['website_cta_url'])
        if'stage_id'invalsand'kanban_state'notinvals:
            vals['kanban_state']='normal'
        ifvals.get('stage_id'):
            stage=self.env['event.track.stage'].browse(vals['stage_id'])
            self._synchronize_with_stage(stage)
        res=super(Track,self).write(vals)
        ifvals.get('partner_id'):
            self.message_subscribe([vals['partner_id']])
        returnres

    @api.model
    def_read_group_stage_ids(self,stages,domain,order):
        """Alwaysdisplayallstages"""
        returnstages.search([],order=order)

    def_synchronize_with_stage(self,stage):
        ifstage.is_done:
            self.is_published=True
        elifstage.is_cancel:
            self.is_published=False

    #------------------------------------------------------------
    #MESSAGING
    #------------------------------------------------------------

    def_track_template(self,changes):
        res=super(Track,self)._track_template(changes)
        track=self[0]
        if'stage_id'inchangesandtrack.stage_id.mail_template_id:
            res['stage_id']=(track.stage_id.mail_template_id,{
                'composition_mode':'comment',
                'auto_delete_message':True,
                'subtype_id':self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
                'email_layout_xmlid':'mail.mail_notification_light'
            })
        returnres

    def_track_subtype(self,init_values):
        self.ensure_one()
        if'kanban_state'ininit_valuesandself.kanban_state=='blocked':
            returnself.env.ref('website_event_track.mt_track_blocked')
        elif'kanban_state'ininit_valuesandself.kanban_state=='done':
            returnself.env.ref('website_event_track.mt_track_ready')
        returnsuper(Track,self)._track_subtype(init_values)

    def_message_get_suggested_recipients(self):
        recipients=super(Track,self)._message_get_suggested_recipients()
        fortrackinself:
            iftrack.partner_emailandtrack.partner_email!=track.partner_id.email:
                track._message_add_suggested_recipient(recipients,email=track.partner_email,reason=_('SpeakerEmail'))
        returnrecipients

    def_message_post_after_hook(self,message,msg_vals):
        ifself.partner_emailandnotself.partner_id:
            #weconsiderthatpostingamessagewithaspecifiedrecipient(notafollower,aspecificone)
            #onadocumentwithoutcustomermeansthatitwascreatedthroughthechatterusing
            #suggestedrecipients.ThisheuristicallowstoavoiduglyhacksinJS.
            email_normalized=tools.email_normalize(self.partner_email)
            new_partner=message.partner_ids.filtered(
                lambdapartner:partner.email==self.partner_emailor(email_normalizedandpartner.email_normalized==email_normalized)
            )
            ifnew_partner:
                ifnew_partner[0].email_normalized:
                    email_domain=('partner_email','in',[new_partner[0].email,new_partner[0].email_normalized])
                else:
                    email_domain=('partner_email','=',new_partner[0].email)
                self.search([
                    ('partner_id','=',False),email_domain,('stage_id.is_cancel','=',False),
                ]).write({'partner_id':new_partner[0].id})
        returnsuper(Track,self)._message_post_after_hook(message,msg_vals)

    #------------------------------------------------------------
    #ACTION
    #------------------------------------------------------------

    defopen_track_speakers_list(self):
        return{
            'name':_('Speakers'),
            'domain':[('id','in',self.mapped('partner_id').ids)],
            'view_mode':'kanban,form',
            'res_model':'res.partner',
            'view_id':False,
            'type':'ir.actions.act_window',
        }

    defget_backend_menu_id(self):
        returnself.env.ref('event.event_main_menu').id

    #------------------------------------------------------------
    #TOOLS
    #------------------------------------------------------------

    def_get_event_track_visitors(self,force_create=False):
        self.ensure_one()

        force_visitor_create=self.env.user._is_public()
        visitor_sudo=self.env['website.visitor']._get_visitor_from_request(force_create=force_visitor_create)
        ifvisitor_sudo:
            visitor_sudo._update_visitor_last_visit()

        ifself.env.user._is_public():
            domain=[('visitor_id','=',visitor_sudo.id)]
        elifvisitor_sudo:
            domain=[
                '|',
                ('partner_id','=',self.env.user.partner_id.id),
                ('visitor_id','=',visitor_sudo.id)
            ]
        else:
            domain=[('partner_id','=',self.env.user.partner_id.id)]

        track_visitors=self.env['event.track.visitor'].sudo().search(
            expression.AND([domain,[('track_id','in',self.ids)]])
        )
        missing=self-track_visitors.track_id
        ifmissingandforce_create:
            track_visitors+=self.env['event.track.visitor'].sudo().create([{
                'visitor_id':visitor_sudo.id,
                'partner_id':self.env.user.partner_id.idifnotself.env.user._is_public()elseFalse,
                'track_id':track.id,
            }fortrackinmissing])

        returntrack_visitors

    def_get_track_suggestions(self,restrict_domain=None,limit=None):
        """Returnsthenexttrackssuggestedaftergoingtothecurrentone
        givenbyself.Tracksalwaysbelongtothesameevent.

        Heuristicis

          *livefirst;
          *thenorderedbystartdate,finishedbeingsenttotheend;
          *wishlisted(manuallyorbydefault);
          *tagmatchingwithcurrenttrack;
          *locationmatchingwithcurrenttrack;
          *finallyarandomtohavean"equivalentwave"randomlygiven;

        :paramrestrict_domain:anadditionaldomaintorestrictcandidates;
        :paramlimit:numberoftrackstoreturn;
        """
        self.ensure_one()

        base_domain=[
            '&',
            ('event_id','=',self.event_id.id),
            ('id','!=',self.id),
        ]
        ifrestrict_domain:
            base_domain=expression.AND([
                base_domain,
                restrict_domain
            ])

        track_candidates=self.search(base_domain,limit=None,order='dateasc')
        ifnottrack_candidates:
            returntrack_candidates

        track_candidates=track_candidates.sorted(
            lambdatrack:
                (track.is_published,
                 track.track_start_remaining==0 #Firstgetthetracksthatstartedlessthan10minutesago...
                 andtrack.track_start_relative<(10*60)
                 andnottrack.is_track_done, #...ANDnotfinished
                 track.track_start_remaining>0, #Thentheonethatwillbeginlater(thesoonercomefirst)
                 -1*track.track_start_remaining,
                 track.is_reminder_on,
                 nottrack.wishlisted_by_default,
                 len(track.tag_ids&self.tag_ids),
                 track.location_id==self.location_id,
                 randint(0,20),
                ),reverse=True
        )

        returntrack_candidates[:limit]
