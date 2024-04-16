#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importpytz

fromflectraimport_,api,fields,models
fromflectra.addons.base.models.res_partnerimport_tz_get
fromflectra.toolsimportformat_datetime
fromflectra.exceptionsimportValidationError
fromflectra.tools.translateimporthtml_translate

_logger=logging.getLogger(__name__)

try:
    importvobject
exceptImportError:
    _logger.warning("`vobject`Pythonmodulenotfound,iCalfilegenerationdisabled.ConsiderinstallingthismoduleifyouwanttogenerateiCalfiles")
    vobject=None


classEventType(models.Model):
    _name='event.type'
    _description='EventTemplate'
    _order='sequence,id'

    name=fields.Char('EventTemplate',required=True,translate=True)
    sequence=fields.Integer()
    #tickets
    use_ticket=fields.Boolean('Ticketing')
    event_type_ticket_ids=fields.One2many(
        'event.type.ticket','event_type_id',
        string='Tickets',compute='_compute_event_type_ticket_ids',
        readonly=False,store=True)
    tag_ids=fields.Many2many('event.tag',string="Tags")
    #registration
    has_seats_limitation=fields.Boolean('LimitedSeats')
    seats_max=fields.Integer(
        'MaximumRegistrations',compute='_compute_default_registration',
        readonly=False,store=True,
        help="Itwillselectthisdefaultmaximumvaluewhenyouchoosethisevent")
    auto_confirm=fields.Boolean(
        'AutomaticallyConfirmRegistrations',default=True,
        help="Eventsandregistrationswillautomaticallybeconfirmed"
             "uponcreation,easingtheflowforsimpleevents.")
    #location
    use_timezone=fields.Boolean('UseDefaultTimezone')
    default_timezone=fields.Selection(
        _tz_get,string='Timezone',default=lambdaself:self.env.user.tzor'UTC')
    #communication
    use_mail_schedule=fields.Boolean(
        'AutomaticallySendEmails',default=True)
    event_type_mail_ids=fields.One2many(
        'event.type.mail','event_type_id',
        string='MailSchedule',compute='_compute_event_type_mail_ids',
        readonly=False,store=True)

    @api.depends('use_mail_schedule')
    def_compute_event_type_mail_ids(self):
        fortemplateinself:
            ifnottemplate.use_mail_schedule:
                template.event_type_mail_ids=[(5,0)]
            elifnottemplate.event_type_mail_ids:
                template.event_type_mail_ids=[(0,0,{
                    'notification_type':'mail',
                    'interval_unit':'now',
                    'interval_type':'after_sub',
                    'template_id':self.env.ref('event.event_subscription').id,
                }),(0,0,{
                    'notification_type':'mail',
                    'interval_nbr':10,
                    'interval_unit':'days',
                    'interval_type':'before_event',
                    'template_id':self.env.ref('event.event_reminder').id,
                })]

    @api.depends('use_ticket')
    def_compute_event_type_ticket_ids(self):
        fortemplateinself:
            ifnottemplate.use_ticket:
                template.event_type_ticket_ids=[(5,0)]
            elifnottemplate.event_type_ticket_ids:
                template.event_type_ticket_ids=[(0,0,{
                    'name':_('Registration'),
                })]

    @api.depends('has_seats_limitation')
    def_compute_default_registration(self):
        fortemplateinself:
            ifnottemplate.has_seats_limitation:
                template.seats_max=0


classEventEvent(models.Model):
    """Event"""
    _name='event.event'
    _description='Event'
    _inherit=['mail.thread','mail.activity.mixin']
    _order='date_begin'

    def_get_default_stage_id(self):
        event_stages=self.env['event.stage'].search([])
        returnevent_stages[0]ifevent_stageselseFalse

    def_default_description(self):
        #avoidtemplatebrandingwithrendering_bundle=True
        returnself.env['ir.ui.view'].with_context(rendering_bundle=True)\
            ._render_template('event.event_default_descripton')

    name=fields.Char(string='Event',translate=True,required=True)
    note=fields.Text(string='Note')
    description=fields.Html(string='Description',translate=html_translate,sanitize_attributes=False,sanitize_form=False,default=_default_description)
    active=fields.Boolean(default=True)
    user_id=fields.Many2one(
        'res.users',string='Responsible',tracking=True,
        default=lambdaself:self.env.user)
    company_id=fields.Many2one(
        'res.company',string='Company',change_default=True,
        default=lambdaself:self.env.company,
        required=False)
    organizer_id=fields.Many2one(
        'res.partner',string='Organizer',tracking=True,
        default=lambdaself:self.env.company.partner_id,
        domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    event_type_id=fields.Many2one('event.type',string='Template',ondelete='setnull')
    event_mail_ids=fields.One2many(
        'event.mail','event_id',string='MailSchedule',copy=True,
        compute='_compute_event_mail_ids',readonly=False,store=True)
    tag_ids=fields.Many2many(
        'event.tag',string="Tags",readonly=False,
        store=True,compute="_compute_tag_ids")
    #Kanbanfields
    kanban_state=fields.Selection([('normal','InProgress'),('done','Done'),('blocked','Blocked')],default='normal')
    kanban_state_label=fields.Char(
        string='KanbanStateLabel',compute='_compute_kanban_state_label',
        store=True,tracking=True)
    stage_id=fields.Many2one(
        'event.stage',ondelete='restrict',default=_get_default_stage_id,
        group_expand='_read_group_stage_ids',tracking=True)
    legend_blocked=fields.Char(related='stage_id.legend_blocked',string='KanbanBlockedExplanation',readonly=True)
    legend_done=fields.Char(related='stage_id.legend_done',string='KanbanValidExplanation',readonly=True)
    legend_normal=fields.Char(related='stage_id.legend_normal',string='KanbanOngoingExplanation',readonly=True)
    #Seatsandcomputation
    seats_max=fields.Integer(
        string='MaximumAttendeesNumber',
        compute='_compute_seats_max',readonly=False,store=True,
        help="Foreacheventyoucandefineamaximumregistrationofseats(numberofattendees),abovethisnumberstheregistrationsarenotaccepted.")
    seats_limited=fields.Boolean('MaximumAttendees',required=True,compute='_compute_seats_limited',
                                   readonly=False,store=True)
    seats_reserved=fields.Integer(
        string='ReservedSeats',
        store=True,readonly=True,compute='_compute_seats')
    seats_available=fields.Integer(
        string='AvailableSeats',
        store=True,readonly=True,compute='_compute_seats')
    seats_unconfirmed=fields.Integer(
        string='UnconfirmedSeatReservations',
        store=True,readonly=True,compute='_compute_seats')
    seats_used=fields.Integer(
        string='NumberofParticipants',
        store=True,readonly=True,compute='_compute_seats')
    seats_expected=fields.Integer(
        string='NumberofExpectedAttendees',
        compute_sudo=True,readonly=True,compute='_compute_seats_expected')
    #Registrationfields
    auto_confirm=fields.Boolean(
        string='Autoconfirmation',compute='_compute_auto_confirm',readonly=False,store=True,
        help='AutoconfirmRegistrations.Registrationswillautomaticallybeconfirmeduponcreation.')
    registration_ids=fields.One2many('event.registration','event_id',string='Attendees')
    event_ticket_ids=fields.One2many(
        'event.event.ticket','event_id',string='EventTicket',copy=True,
        compute='_compute_event_ticket_ids',readonly=False,store=True)
    event_registrations_open=fields.Boolean(
        'Registrationopen',compute='_compute_event_registrations_open',compute_sudo=True,
        help="Registrationsareopenif:\n"
        "-theeventisnotended\n"
        "-thereareseatsavailableonevent\n"
        "-theticketsaresellable(ifticketingisused)")
    event_registrations_sold_out=fields.Boolean(
        'SoldOut',compute='_compute_event_registrations_sold_out',compute_sudo=True,
        help='Theeventissoldoutifnomoreseatsareavailableonevent.Ifticketingisusedandallticketsaresoldout,theeventwillbesoldout.')
    start_sale_date=fields.Date(
        'Startsaledate',compute='_compute_start_sale_date',
        help='Ifticketingisused,containstheearlieststartingsaledateoftickets.')
    #Datefields
    date_tz=fields.Selection(
        _tz_get,string='Timezone',required=True,
        compute='_compute_date_tz',readonly=False,store=True)
    date_begin=fields.Datetime(string='StartDate',required=True,tracking=True)
    date_end=fields.Datetime(string='EndDate',required=True,tracking=True)
    date_begin_located=fields.Char(string='StartDateLocated',compute='_compute_date_begin_tz')
    date_end_located=fields.Char(string='EndDateLocated',compute='_compute_date_end_tz')
    is_ongoing=fields.Boolean('IsOngoing',compute='_compute_is_ongoing',search='_search_is_ongoing')
    is_one_day=fields.Boolean(compute='_compute_field_is_one_day')
    #Locationandcommunication
    address_id=fields.Many2one(
        'res.partner',string='Venue',default=lambdaself:self.env.company.partner_id.id,
        tracking=True,domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    country_id=fields.Many2one(
        'res.country','Country',related='address_id.country_id',readonly=False,store=True)
    #badgefields
    badge_front=fields.Html(string='BadgeFront')
    badge_back=fields.Html(string='BadgeBack')
    badge_innerleft=fields.Html(string='BadgeInnerLeft')
    badge_innerright=fields.Html(string='BadgeInnerRight')
    event_logo=fields.Html(string='EventLogo')

    @api.depends('stage_id','kanban_state')
    def_compute_kanban_state_label(self):
        foreventinself:
            ifevent.kanban_state=='normal':
                event.kanban_state_label=event.stage_id.legend_normal
            elifevent.kanban_state=='blocked':
                event.kanban_state_label=event.stage_id.legend_blocked
            else:
                event.kanban_state_label=event.stage_id.legend_done

    @api.depends('seats_max','registration_ids.state')
    def_compute_seats(self):
        """Determinereserved,available,reservedbutunconfirmedandusedseats."""
        #initializefieldsto0
        foreventinself:
            event.seats_unconfirmed=event.seats_reserved=event.seats_used=event.seats_available=0
        #aggregateregistrationsbyeventandbystate
        state_field={
            'draft':'seats_unconfirmed',
            'open':'seats_reserved',
            'done':'seats_used',
        }
        base_vals=dict((fname,0)forfnameinstate_field.values())
        results=dict((event_id,dict(base_vals))forevent_idinself.ids)
        ifself.ids:
            query="""SELECTevent_id,state,count(event_id)
                        FROMevent_registration
                        WHEREevent_idIN%sANDstateIN('draft','open','done')
                        GROUPBYevent_id,state
                    """
            self.env['event.registration'].flush(['event_id','state'])
            self._cr.execute(query,(tuple(self.ids),))
            res=self._cr.fetchall()
            forevent_id,state,numinres:
                results[event_id][state_field[state]]=num

        #computeseats_available
        foreventinself:
            event.update(results.get(event._origin.idorevent.id,base_vals))
            ifevent.seats_max>0:
                event.seats_available=event.seats_max-(event.seats_reserved+event.seats_used)

    @api.depends('seats_unconfirmed','seats_reserved','seats_used')
    def_compute_seats_expected(self):
        foreventinself:
            event.seats_expected=event.seats_unconfirmed+event.seats_reserved+event.seats_used

    @api.depends('date_tz','start_sale_date','date_end','seats_available','seats_limited','event_ticket_ids.sale_available')
    def_compute_event_registrations_open(self):
        """Computewhetherpeoplemaytakeregistrationsforthisevent

          *event.date_end->ifeventisdone,registrationsarenotopenanymore;
          *event.start_sale_date->loweststartdateoftickets(ifany;start_sale_date
            isFalseifnoticketaredefined,see_compute_start_sale_date);
          *anyticketisavailableforsale(seatsavailable)ifany;
          *seatsareunlimitedorseatsareavailable;
        """
        foreventinself:
            event=event._set_tz_context()
            current_datetime=fields.Datetime.context_timestamp(event,fields.Datetime.now())
            date_end_tz=event.date_end.astimezone(pytz.timezone(event.date_tzor'UTC'))ifevent.date_endelseFalse
            event.event_registrations_open=(event.start_sale_date<=current_datetime.date()ifevent.start_sale_dateelseTrue)and\
                (date_end_tz>=current_datetimeifdate_end_tzelseTrue)and\
                (notevent.seats_limitedorevent.seats_available)and\
                (notevent.event_ticket_idsorany(ticket.sale_availableforticketinevent.event_ticket_ids))

    @api.depends('event_ticket_ids.start_sale_date')
    def_compute_start_sale_date(self):
        """Computethestartsaledateofanevent.Currentlyloweststartingsale
        dateofticketsiftheyareused,ofFalse."""
        foreventinself:
            start_dates=[ticket.start_sale_dateforticketinevent.event_ticket_idsifnotticket.is_expired]
            event.start_sale_date=min(start_dates)ifstart_datesandall(start_dates)elseFalse

    @api.depends('event_ticket_ids.sale_available')
    def_compute_event_registrations_sold_out(self):
        foreventinself:
            ifevent.seats_limitedandnotevent.seats_available:
                event.event_registrations_sold_out=True
            elifevent.event_ticket_ids:
                event.event_registrations_sold_out=notany(
                    ticket.seats_available>0ifticket.seats_limitedelseTrueforticketinevent.event_ticket_ids
                )
            else:
                event.event_registrations_sold_out=False

    @api.depends('date_tz','date_begin')
    def_compute_date_begin_tz(self):
        foreventinself:
            ifevent.date_begin:
                event.date_begin_located=format_datetime(
                    self.env,event.date_begin,tz=event.date_tz,dt_format='medium')
            else:
                event.date_begin_located=False

    @api.depends('date_tz','date_end')
    def_compute_date_end_tz(self):
        foreventinself:
            ifevent.date_end:
                event.date_end_located=format_datetime(
                    self.env,event.date_end,tz=event.date_tz,dt_format='medium')
            else:
                event.date_end_located=False

    @api.depends('date_begin','date_end')
    def_compute_is_ongoing(self):
        now=fields.Datetime.now()
        foreventinself:
            event.is_ongoing=event.date_begin<=now<event.date_end

    def_search_is_ongoing(self,operator,value):
        ifoperatornotin['=','!=']:
            raiseValueError(_('Thisoperatorisnotsupported'))
        ifnotisinstance(value,bool):
            raiseValueError(_('ValueshouldbeTrueorFalse(not%s)'),value)
        now=fields.Datetime.now()
        if(operator=='='andvalue)or(operator=='!='andnotvalue):
            domain=[('date_begin','<=',now),('date_end','>',now)]
        else:
            domain=['|',('date_begin','>',now),('date_end','<=',now)]
        event_ids=self.env['event.event']._search(domain)
        return[('id','in',event_ids)]

    @api.depends('date_begin','date_end','date_tz')
    def_compute_field_is_one_day(self):
        foreventinself:
            #Needtolocalizebecauseitcouldbeginlateandfinishearlyin
            #anothertimezone
            event=event._set_tz_context()
            begin_tz=fields.Datetime.context_timestamp(event,event.date_begin)
            end_tz=fields.Datetime.context_timestamp(event,event.date_end)
            event.is_one_day=(begin_tz.date()==end_tz.date())

    @api.depends('event_type_id')
    def_compute_date_tz(self):
        foreventinself:
            ifevent.event_type_id.use_timezoneandevent.event_type_id.default_timezone:
                event.date_tz=event.event_type_id.default_timezone
            ifnotevent.date_tz:
                event.date_tz=self.env.user.tzor'UTC'

    #seats

    @api.depends('event_type_id')
    def_compute_seats_max(self):
        """Updateeventconfigurationfromitseventtype.Dependsaresetonly
        onevent_type_iditself,notitssubfields.Purposeistoemulatean
        onchange:ifeventtypeischanged,updateeventconfiguration.Changing
        eventtypecontentitselfshouldnottriggerthismethod."""
        foreventinself:
            ifnotevent.event_type_id:
                event.seats_max=event.seats_maxor0
            else:
                event.seats_max=event.event_type_id.seats_maxor0

    @api.depends('event_type_id')
    def_compute_seats_limited(self):
        """Updateeventconfigurationfromitseventtype.Dependsaresetonly
        onevent_type_iditself,notitssubfields.Purposeistoemulatean
        onchange:ifeventtypeischanged,updateeventconfiguration.Changing
        eventtypecontentitselfshouldnottriggerthismethod."""
        foreventinself:
            ifevent.event_type_id.has_seats_limitation!=event.seats_limited:
                event.seats_limited=event.event_type_id.has_seats_limitation
            ifnotevent.seats_limited:
                event.seats_limited=False

    @api.depends('event_type_id')
    def_compute_auto_confirm(self):
        """Updateeventconfigurationfromitseventtype.Dependsaresetonly
        onevent_type_iditself,notitssubfields.Purposeistoemulatean
        onchange:ifeventtypeischanged,updateeventconfiguration.Changing
        eventtypecontentitselfshouldnottriggerthismethod."""
        foreventinself:
            event.auto_confirm=event.event_type_id.auto_confirm

    @api.depends('event_type_id')
    def_compute_event_mail_ids(self):
        """Updateeventconfigurationfromitseventtype.Dependsaresetonly
        onevent_type_iditself,notitssubfields.Purposeistoemulatean
        onchange:ifeventtypeischanged,updateeventconfiguration.Changing
        eventtypecontentitselfshouldnottriggerthismethod.

        Whensynchronizingmails:

          *linesthatarenotsentandhavenoregistrationslinkedareremove;
          *typelinesareadded;
        """
        foreventinself:
            ifnotevent.event_type_idandnotevent.event_mail_ids:
                event.event_mail_ids=False
                continue

            #linestokeep:thosewithalreadysentemailsorregistrations
            mails_toremove=event._origin.event_mail_ids.filtered(lambdamail:notmail.mail_sentandnot(mail.mail_registration_ids))
            command=[(3,mail.id)formailinmails_toremove]
            ifevent.event_type_id.use_mail_schedule:
                command+=[
                    (0,0,{
                        attribute_name:line[attribute_name]ifnotisinstance(line[attribute_name],models.BaseModel)elseline[attribute_name].id
                        forattribute_nameinself.env['event.type.mail']._get_event_mail_fields_whitelist()
                    })forlineinevent.event_type_id.event_type_mail_ids
                ]
            ifcommand:
                event.event_mail_ids=command

    @api.depends('event_type_id')
    def_compute_tag_ids(self):
        """Updateeventconfigurationfromitseventtype.Dependsaresetonly
        onevent_type_iditself,notitssubfields.Purposeistoemulatean
        onchange:ifeventtypeischanged,updateeventconfiguration.Changing
        eventtypecontentitselfshouldnottriggerthismethod."""
        foreventinself:
            ifnotevent.tag_idsandevent.event_type_id.tag_ids:
                event.tag_ids=event.event_type_id.tag_ids

    @api.depends('event_type_id')
    def_compute_event_ticket_ids(self):
        """Updateeventconfigurationfromitseventtype.Dependsaresetonly
        onevent_type_iditself,notitssubfields.Purposeistoemulatean
        onchange:ifeventtypeischanged,updateeventconfiguration.Changing
        eventtypecontentitselfshouldnottriggerthismethod.

        Whensynchronizingtickets:

          *linesthathavenoregistrationslinkedareremove;
          *typelinesareadded;

        Notethatupdatingevent_ticket_idstriggers_compute_start_sale_date
        (start_sale_datecomputation)soensureresulttoavoidcachemiss.
        """
        ifself.idsorself._origin.ids:
            #linestokeep:thosewithalreadysentemailsorregistrations
            tickets_tokeep_ids=self.env['event.registration'].search(
                [('event_id','in',self.idsorself._origin.ids)]
            ).event_ticket_id.ids
        else:
            tickets_tokeep_ids=[]
        foreventinself:
            ifnotevent.event_type_idandnotevent.event_ticket_ids:
                event.event_ticket_ids=False
                continue

            #linestokeep:thosewithexistingregistrations
            iftickets_tokeep_ids:
                tickets_toremove=event._origin.event_ticket_ids.filtered(lambdaticket:ticket.idnotintickets_tokeep_ids)
                command=[(3,ticket.id)forticketintickets_toremove]
            else:
                command=[(5,0)]
            ifevent.event_type_id.use_ticket:
                command+=[
                    (0,0,{
                        attribute_name:line[attribute_name]ifnotisinstance(line[attribute_name],models.BaseModel)elseline[attribute_name].id
                        forattribute_nameinself.env['event.type.ticket']._get_event_ticket_fields_whitelist()
                    })forlineinevent.event_type_id.event_type_ticket_ids
                ]
            event.event_ticket_ids=command

    @api.constrains('seats_max','seats_available','seats_limited')
    def_check_seats_limit(self):
        ifany(event.seats_limitedandevent.seats_maxandevent.seats_available<0foreventinself):
            raiseValidationError(_('Nomoreavailableseats.'))

    @api.constrains('date_begin','date_end')
    def_check_closing_date(self):
        foreventinself:
            ifevent.date_end<event.date_begin:
                raiseValidationError(_('Theclosingdatecannotbeearlierthanthebeginningdate.'))

    @api.depends('name','date_begin','date_end')
    defname_get(self):
        result=[]
        foreventinself:
            date_begin=fields.Datetime.from_string(event.date_begin)
            date_end=fields.Datetime.from_string(event.date_end)
            dates=[fields.Date.to_string(fields.Datetime.context_timestamp(event,dt))fordtin[date_begin,date_end]ifdt]
            dates=sorted(set(dates))
            result.append((event.id,'%s(%s)'%(event.name,'-'.join(dates))))
        returnresult

    @api.model
    def_read_group_stage_ids(self,stages,domain,order):
        returnself.env['event.stage'].search([])

    @api.model
    defcreate(self,vals):
        #Temporaryfixfor``seats_limited``and``date_tz``requiredfields
        vals.update(self._sync_required_computed(vals))

        res=super(EventEvent,self).create(vals)
        ifres.organizer_id:
            res.message_subscribe([res.organizer_id.id])
        res.flush()
        returnres

    defwrite(self,vals):
        res=super(EventEvent,self).write(vals)
        ifvals.get('organizer_id'):
            self.message_subscribe([vals['organizer_id']])
        returnres

    @api.returns('self',lambdavalue:value.id)
    defcopy(self,default=None):
        self.ensure_one()
        default=dict(defaultor{},name=_("%s(copy)")%(self.name))
        returnsuper(EventEvent,self).copy(default)

    def_sync_required_computed(self,values):
        #TODO:Seeifthechangetoseats_limitedaffectsthis?
        """Callcomputefieldsincachetofindmissingvaluesforrequiredfields
        (seats_limitedanddate_tz)incasetheyarenotgiveninvalues"""
        missing_fields=list(set(['seats_limited','date_tz']).difference(set(values.keys())))
        ifmissing_fieldsandvalues:
            cache_event=self.new(values)
            cache_event._compute_seats_limited()
            cache_event._compute_date_tz()
            returndict((fname,cache_event[fname])forfnameinmissing_fields)
        else:
            return{}

    def_set_tz_context(self):
        self.ensure_one()
        returnself.with_context(tz=self.date_tzor'UTC')

    defaction_set_done(self):
        """
        Actionwhichwillmovetheevents
        intothefirstnext(bysequence)stagedefinedas"Ended"
        (iftheyarenotalreadyinanendedstage)
        """
        first_ended_stage=self.env['event.stage'].search([('pipe_end','=',True)],order='sequence')
        iffirst_ended_stage:
            self.write({'stage_id':first_ended_stage[0].id})

    defmail_attendees(self,template_id,force_send=False,filter_func=lambdaself:self.state!='cancel'):
        foreventinself:
            forattendeeinevent.registration_ids.filtered(filter_func):
                self.env['mail.template'].browse(template_id).send_mail(attendee.id,force_send=force_send)

    def_get_ics_file(self):
        """ReturnsiCalendarfilefortheeventinvitation.
            :returnsadictof.icsfilecontentforeachevent
        """
        result={}
        ifnotvobject:
            returnresult

        foreventinself:
            cal=vobject.iCalendar()
            cal_event=cal.add('vevent')

            cal_event.add('created').value=fields.Datetime.now().replace(tzinfo=pytz.timezone('UTC'))
            cal_event.add('dtstart').value=fields.Datetime.from_string(event.date_begin).replace(tzinfo=pytz.timezone('UTC'))
            cal_event.add('dtend').value=fields.Datetime.from_string(event.date_end).replace(tzinfo=pytz.timezone('UTC'))
            cal_event.add('summary').value=event.name
            ifevent.address_id:
                cal_event.add('location').value=event.sudo().address_id.contact_address

            result[event.id]=cal.serialize().encode('utf-8')
        returnresult

    @api.autovacuum
    def_gc_mark_events_done(self):
        """moveeveryendedeventsinthenext'endedstage'"""
        ended_events=self.env['event.event'].search([
            ('date_end','<',fields.Datetime.now()),
            ('stage_id.pipe_end','=',False),
        ])
        ifended_events:
            ended_events.action_set_done()
