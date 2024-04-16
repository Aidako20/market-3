#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError,UserError


classEventTemplateTicket(models.Model):
    _name='event.type.ticket'
    _description='EventTemplateTicket'

    #description
    name=fields.Char(
        string='Name',default=lambdaself:_('Registration'),
        required=True,translate=True)
    description=fields.Text(
        'Description',translate=True,
        help="Adescriptionoftheticketthatyouwanttocommunicatetoyourcustomers.")
    event_type_id=fields.Many2one(
        'event.type',string='EventCategory',ondelete='cascade',required=True)
    #seats
    seats_limited=fields.Boolean(string='SeatsLimit',readonly=True,store=True,
                                   compute='_compute_seats_limited')
    seats_max=fields.Integer(
        string='MaximumSeats',
        help="Definethenumberofavailabletickets.Ifyouhavetoomanyregistrationsyouwill"
             "notbeabletosellticketsanymore.Set0toignorethisrulesetasunlimited.")

    @api.depends('seats_max')
    def_compute_seats_limited(self):
        forticketinself:
            ticket.seats_limited=ticket.seats_max

    @api.model
    def_get_event_ticket_fields_whitelist(self):
        """Whitelistoffieldsthatarecopiedfromevent_type_ticket_idstoevent_ticket_idswhen
        changingtheevent_type_idfieldofevent.event"""
        return['name','description','seats_max']


classEventTicket(models.Model):
    """Ticketmodelallowingtohavedifferntkindofregistrationsforagiven
    event.Ticketarebasedontickettypeastheysharesomecommonfields
    andbehavior.Thosemodelscomefrom<=v13Flectraevent.event.ticketthat
    modeledbothconcept:ticketsforeventtemplates,andticketsforevents."""
    _name='event.event.ticket'
    _inherit='event.type.ticket'
    _description='EventTicket'

    @api.model
    defdefault_get(self,fields):
        res=super(EventTicket,self).default_get(fields)
        if'name'infieldsand(notres.get('name')orres['name']==_('Registration'))andself.env.context.get('default_event_name'):
            res['name']=_('Registrationfor%s',self.env.context['default_event_name'])
        returnres

    #description
    event_type_id=fields.Many2one(ondelete='setnull',required=False)
    event_id=fields.Many2one(
        'event.event',string="Event",
        ondelete='cascade',required=True)
    company_id=fields.Many2one('res.company',related='event_id.company_id')
    #sale
    start_sale_date=fields.Date(string="RegistrationStart")
    end_sale_date=fields.Date(string="RegistrationEnd")
    is_expired=fields.Boolean(string='IsExpired',compute='_compute_is_expired')
    sale_available=fields.Boolean(string='IsAvailable',compute='_compute_sale_available',compute_sudo=True)
    registration_ids=fields.One2many('event.registration','event_ticket_id',string='Registrations')
    #seats
    seats_reserved=fields.Integer(string='ReservedSeats',compute='_compute_seats',store=True)
    seats_available=fields.Integer(string='AvailableSeats',compute='_compute_seats',store=True)
    seats_unconfirmed=fields.Integer(string='UnconfirmedSeats',compute='_compute_seats',store=True)
    seats_used=fields.Integer(string='UsedSeats',compute='_compute_seats',store=True)

    @api.depends('end_sale_date','event_id.date_tz')
    def_compute_is_expired(self):
        forticketinself:
            ticket=ticket._set_tz_context()
            current_date=fields.Date.context_today(ticket)
            ifticket.end_sale_date:
                ticket.is_expired=ticket.end_sale_date<current_date
            else:
                ticket.is_expired=False

    @api.depends('is_expired','start_sale_date','event_id.date_tz','seats_available','seats_max')
    def_compute_sale_available(self):
        forticketinself:
            ifnotticket.is_launched()orticket.is_expiredor(ticket.seats_maxandticket.seats_available<=0):
                ticket.sale_available=False
            else:
                ticket.sale_available=True

    @api.depends('seats_max','registration_ids.state')
    def_compute_seats(self):
        """Determinereserved,available,reservedbutunconfirmedandusedseats."""
        #initializefieldsto0+computeseatsavailability
        forticketinself:
            ticket.seats_unconfirmed=ticket.seats_reserved=ticket.seats_used=ticket.seats_available=0
        #aggregateregistrationsbyticketandbystate
        results={}
        ifself.ids:
            state_field={
                'draft':'seats_unconfirmed',
                'open':'seats_reserved',
                'done':'seats_used',
            }
            query="""SELECTevent_ticket_id,state,count(event_id)
                        FROMevent_registration
                        WHEREevent_ticket_idIN%sANDstateIN('draft','open','done')
                        GROUPBYevent_ticket_id,state
                    """
            self.env['event.registration'].flush(['event_id','event_ticket_id','state'])
            self.env.cr.execute(query,(tuple(self.ids),))
            forevent_ticket_id,state,numinself.env.cr.fetchall():
                results.setdefault(event_ticket_id,{})[state_field[state]]=num

        #computeseats_available
        forticketinself:
            ticket.update(results.get(ticket._origin.idorticket.id,{}))
            ifticket.seats_max>0:
                ticket.seats_available=ticket.seats_max-(ticket.seats_reserved+ticket.seats_used)

    @api.constrains('start_sale_date','end_sale_date')
    def_constrains_dates_coherency(self):
        forticketinself:
            ifticket.start_sale_dateandticket.end_sale_dateandticket.start_sale_date>ticket.end_sale_date:
                raiseUserError(_('Thestopdatecannotbeearlierthanthestartdate.'))

    @api.constrains('seats_available','seats_max')
    def_constrains_seats_available(self):
        ifany(record.seats_maxandrecord.seats_available<0forrecordinself):
            raiseValidationError(_('Nomoreavailableseatsforthisticket.'))

    def_get_ticket_multiline_description(self):
        """Computeamultilinedescriptionofthisticket.Itisusedwhenticket
        descriptionarenecessarywithouthavingtoencodeitmanually,likesales
        information."""
        return'%s\n%s'%(self.display_name,self.event_id.display_name)

    def_set_tz_context(self):
        self.ensure_one()
        returnself.with_context(tz=self.event_id.date_tzor'UTC')

    defis_launched(self):
        #TDEFIXME:inmaster,makeacomputedfield,easiertouse
        self.ensure_one()
        ifself.start_sale_date:
            ticket=self._set_tz_context()
            current_date=fields.Date.context_today(ticket)
            returnticket.start_sale_date<=current_date
        else:
            returnTrue
