#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classWebsiteVisitor(models.Model):
    _name='website.visitor'
    _inherit=['website.visitor']

    parent_id=fields.Many2one(
        'website.visitor',string="Parent",ondelete='setnull',
        help="Mainidentity")
    event_registration_ids=fields.One2many(
        'event.registration','visitor_id',string='EventRegistrations',
        groups="event.group_event_user")
    event_registration_count=fields.Integer(
        '#Registrations',compute='_compute_event_registration_count',
        groups="event.group_event_user")
    event_registered_ids=fields.Many2many(
        'event.event',string="RegisteredEvents",
        compute="_compute_event_registered_ids",compute_sudo=True,
        search="_search_event_registered_ids",
        groups="event.group_event_user")

    @api.depends('event_registration_ids')
    def_compute_event_registration_count(self):
        ifself.ids:
            read_group_res=self.env['event.registration'].read_group(
                [('visitor_id','in',self.ids)],
                ['visitor_id'],['visitor_id'])
            visitor_mapping=dict(
                (item['visitor_id'][0],item['visitor_id_count'])
                foriteminread_group_res)
        else:
            visitor_mapping=dict()
        forvisitorinself:
            visitor.event_registration_count=visitor_mapping.get(visitor.id)or0

    @api.depends('event_registration_ids.email','event_registration_ids.mobile','event_registration_ids.phone')
    def_compute_email_phone(self):
        super(WebsiteVisitor,self)._compute_email_phone()
        self.flush()

        forvisitorinself.filtered(lambdavisitor:notvisitor.emailornotvisitor.mobile):
            linked_registrations=visitor.event_registration_ids.sorted(lambdareg:(reg.create_date,reg.id),reverse=False)
            ifnotvisitor.email:
                visitor.email=next((reg.emailforreginlinked_registrationsifreg.email),False)
            ifnotvisitor.mobile:
                visitor.mobile=next((reg.mobileorreg.phoneforreginlinked_registrationsifreg.mobileorreg.phone),False)

    @api.depends('parent_id','event_registration_ids')
    def_compute_event_registered_ids(self):
        #includeparent'sregistrationsinavisitoro2mfield.Wedon'tadd
        #childoneaschildshouldnothaveregistrations(movedtotheparent)
        forvisitorinself:
            all_registrations=visitor.event_registration_ids|visitor.parent_id.event_registration_ids
            visitor.event_registered_ids=all_registrations.mapped('event_id')

    def_search_event_registered_ids(self,operator,operand):
        """Searchvisitorswithtermsoneventswithintheireventregistrations.E.g.[('event_registered_ids',
        'in',[1,2])]shouldreturnvisitorshavingaregistrationonevents1,2as
        wellastheirchildrenfornotificationpurpose."""
        ifoperator=="notin":
            raiseNotImplementedError("Unsupported'NotIn'operationonvisitorsregistrations")

        all_registrations=self.env['event.registration'].sudo().search([
            ('event_id',operator,operand)
        ])
        ifall_registrations:
            #searchchildren,evenarchivedone,tocontactthem
            visitors=all_registrations.with_context(active_test=False).mapped('visitor_id')
            children=self.env['website.visitor'].with_context(
                active_test=False
            ).sudo().search([('parent_id','in',visitors.ids)])
            visitor_ids=(visitors+children).ids
        else:
            visitor_ids=[]

        return[('id','in',visitor_ids)]

    def_link_to_partner(self,partner,update_values=None):
        """Propagatepartnerupdatetoregistrationrecords"""
        ifpartner:
            registration_wo_partner=self.event_registration_ids.filtered(lambdaregistration:notregistration.partner_id)
            ifregistration_wo_partner:
                registration_wo_partner.partner_id=partner
        super(WebsiteVisitor,self)._link_to_partner(partner,update_values=update_values)

    def_link_to_visitor(self,target,keep_unique=True):
        """Overridelinkingprocesstolinkregistrationstothefinalvisitor."""
        self.event_registration_ids.write({'visitor_id':target.id})

        res=super(WebsiteVisitor,self)._link_to_visitor(target,keep_unique=False)

        ifkeep_unique:
            self.partner_id=False
            self.parent_id=target.id
            self.active=False

        returnres

    def_get_visitor_from_request(self,force_create=False):
        """Whenfetchingvisitor,nowthatduplicatesarelinkedtoamainvisitor
        insteadofunlinked,youmayhavemorecollisionsissueswithcookiebeing
        setafterade-connectionforexample.

        Inbasemethod,visitorassociatedtoapartnerincaseofpublicuseris
        nottakenintoaccount.Itisconsideredasdesynchronizedcookie.Here
        wealsodiscardifthevisitorhasamainvisitorwhosepartnerisset
        (akawrongafterlogoutpartner)."""
        visitor=super(WebsiteVisitor,self)._get_visitor_from_request(force_create=force_create)

        #alsocheckthatvisitorparentpartnerisnotdifferentfromuser'sone(indicatesduplicateduetoinvalidorwrongcookie)
        ifvisitorandvisitor.parent_id.partner_id:
            ifself.env.user._is_public():
                visitor=self.env['website.visitor'].sudo()
            elifnotvisitor.partner_id:
                visitor=self.env['website.visitor'].sudo().with_context(active_test=False).search(
                    [('partner_id','=',self.env.user.partner_id.id)]
                )

        ifnotvisitorandforce_create:
            visitor=self._create_visitor()

        returnvisitor
