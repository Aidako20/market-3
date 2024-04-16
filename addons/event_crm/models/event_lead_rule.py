#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromastimportliteral_eval
fromcollectionsimportdefaultdict

fromflectraimportfields,models,_
fromflectra.osvimportexpression


classEventLeadRule(models.Model):
    """Rulemodelforcreating/updatingleadsfromeventregistrations.

    SPECIFICATIONS:CREATIONTYPE

    Therearetwotypesofleadcreation:

      *perattendee:createaleadforeachregistration;
      *perorder:createaleadforagroupofregistrations;

    Thelastoneisonlyavailablethroughinterfaceifitispossibletoregister
    agroupofattendeesinoneaction(whenevent_saleorwebsite_eventare
    installed).Behavioritselfisimplementeddirectlyinevent_crm.

    Basicallyagroupiseitheralistofregistrationsbelongingtothesame
    eventandcreatedinbatch(website_eventflow).Withevent_salethis
    definitionwillbeimprovedtobebasedonsale_order.

    SPECIFICATIONS:CREATIONTRIGGERS

    Therearethreeoptionstotriggerleadcreation.Weconsiderbasicallythat
    leadqualityincreasesifattendeesconfirmedorwenttotheevent.Triggers
    allowthereforetorunrules:

      *atattendeecreation;
      *atattendeeconfirmation;
      *atattendeevenue;

    Thistriggerdefineswhentherulewillrun.

    SPECIFICATIONS:FILTERINGREGISTRATIONS

    Whenabatchofregistrationsmatchestheruletriggerwefilterthembased
    onconditionsandrulesdefinesonevent_lead_rulemodel.Heuristicisthe
    following:

      *theruleisactive;
      *ifafilterisset:filterregistrationsbasedonthisfilter.Thisis
        donelikeasearch,andfilterisadomain;
      *ifacompanyissetontherule,itmustmatchevent'scompany.Note
        thatmulti-companyrulesapplyonevent_lead_rule;
      *ifaneventcategoryitset,itmustmatch;
      *ifaneventisset,itmustmatch;
      *ifbotheventandcategoryareset,oneofthemmustmatch(OR).Ifnone
        ofthoseareset,itisconsideredasOK;

    Ifconditionsaremet,leadsarecreatedwithpre-filledinformationsdefined
    ontherule(type,user_id,team_id).Contactinformationcomingfromthe
    registrationsarecomputed(customer,name,email,phone,mobile,contact_name).

    SPECIFICATIONS:OTHERPOINTS

    Notethatallrulesmatchingtheirconditionsareapplied.Thismeansmore
    thanoneleadcanbecreateddependingontheconfiguration.Thisis
    intendedinordertogivemorefreedomtotheuserusingtheautomatic
    leadgeneration.
    """
    _name="event.lead.rule"
    _description="EventLeadRules"

    #Definition
    name=fields.Char('RuleName',required=True,translate=True)
    active=fields.Boolean('Active',default=True)
    lead_ids=fields.One2many(
        'crm.lead','event_lead_rule_id',string='CreatedLeads',
        groups='sales_team.group_sale_salesman')
    #Triggers
    lead_creation_basis=fields.Selection([
        ('attendee','PerAttendee'),('order','PerOrder')],
        string='Create',default='attendee',required=True,
        help='PerAttendee:ALeadiscreatedforeachAttendee(B2C).\n'
             'PerOrder:AsingleLeadiscreatedperTicketBatch/SaleOrder(B2B)')
    lead_creation_trigger=fields.Selection([
        ('create','Attendeesarecreated'),
        ('confirm','Attendeesareconfirmed'),
        ('done','Attendeesattended')],
        string='When',default='create',required=True,
        help='Creation:atattendeecreation;\n'
             'Confirmation:whenattendeeisconfirmed,manuallyorautomatically;\n'
             'Attended:whenattendanceisconfirmedandregistrationsettodone;')
    #Filters
    event_type_ids=fields.Many2many(
        'event.type',string='EventCategories',
        help='Filtertheattendeestoincludethoseofthisspecificeventcategory.Ifnotset,noeventcategoryrestrictionwillbeapplied.')
    event_id=fields.Many2one(
        'event.event',string='Event',
        domain="[('company_id','in',[company_idorcurrent_company_id,False])]",
        help='Filtertheattendeestoincludethoseofthisspecificevent.Ifnotset,noeventrestrictionwillbeapplied.')
    company_id=fields.Many2one(
        'res.company',string='Company',
        help="Restrictthetriggerofthisruletoeventsbelongingtoaspecificcompany.\nIfnotset,nocompanyrestrictionwillbeapplied.")
    event_registration_filter=fields.Text(string="RegistrationsDomain",help="Filtertheattendeesthatwillornotgenerateleads.")
    #Leaddefault_valuefields
    lead_type=fields.Selection([
        ('lead','Lead'),('opportunity','Opportunity')],string="LeadType",required=True,
        default=lambdaself:'lead'ifself.env['res.users'].has_group('crm.group_use_lead')else'opportunity',
        help="Defaultleadtypewhenthisruleisapplied.")
    lead_sales_team_id=fields.Many2one('crm.team',string='SalesTeam',help="AutomaticallyassignthecreatedleadstothisSalesTeam.")
    lead_user_id=fields.Many2one('res.users',string='Salesperson',help="AutomaticallyassignthecreatedleadstothisSalesperson.")
    lead_tag_ids=fields.Many2many('crm.tag',string='Tags',help="Automaticallyaddthesetagstothecreatedleads.")

    def_run_on_registrations(self,registrations):
        """Createorupdateleadsbasedonruleconfiguration.Twomainlead
        managementtypeexists

          *perattendee:eachregistrationcreatesalead;
          *perorder:registrationsaregroupedpergroupandoneleadiscreated
            orupdatedwiththebatch(usedmainlywithsaleorderconfiguration
            inevent_sale);

        Heuristic

          *first,checkexistingleadlinkedtoregistrationstoensureno
            duplication.Indeedforexampleattendeestatuschangemaytrigger
            thesameruleseveraltimes;
          *thenforeachrule,getthesubsetofregistrationsmatchingits
            filters;
          *thenforeachorder-basedrule,getthegroupinginformation.This
            givealistofregistrationsbygroup(event,sale_order),withmaybe
            analready-existingleadtoupdateinsteadofcreatinganewone;
          *finallyapplyrules.Attendee-basedrulescreatealeadforeach
            attendee,group-basedrulesusethegroupinginformationtocreate
            orupdateleads;

        :paramregistrations:event.registrationrecordsetonwhichrulesgivenby
          selfhavetorun.Triggersshouldalreadybechecked,onlyfiltersare
          appliedhere.

        :returnleads:newly-createdleads.Updatedleadsarenotreturned.
        """
        #orderbyID,ensurefirstcreatedwins
        registrations=registrations.sorted('id')

        #first:ensurenoduplicatebysearchingexistingregistrations/rule
        existing_leads=self.env['crm.lead'].search([
            ('registration_ids','in',registrations.ids),
            ('event_lead_rule_id','in',self.ids)
        ])
        rule_to_existing_regs=defaultdict(lambda:self.env['event.registration'])
        forleadinexisting_leads:
            rule_to_existing_regs[lead.event_lead_rule_id]+=lead.registration_ids

        #second:checkregistrationsmatchingrules(inbatch)
        new_registrations=self.env['event.registration']
        rule_to_new_regs=dict()
        forruleinself:
            new_for_rule=registrations.filtered(lambdareg:regnotinrule_to_existing_regs[rule])
            rule_registrations=rule._filter_registrations(new_for_rule)
            new_registrations|=rule_registrations
            rule_to_new_regs[rule]=rule_registrations
        new_registrations.sorted('id') #asanORwasused,re-ensureorder

        #third:checkgrouping
        order_based_rules=self.filtered(lambdarule:rule.lead_creation_basis=='order')
        rule_group_info=new_registrations._get_lead_grouping(order_based_rules,rule_to_new_regs)

        lead_vals_list=[]
        forruleinself:
            ifrule.lead_creation_basis=='attendee':
                matching_registrations=rule_to_new_regs[rule].sorted('id')
                forregistrationinmatching_registrations:
                    lead_vals_list.append(registration._get_lead_values(rule))
            else:
                #checkifregistrationsarepartofagroup,forexampleasaleorder,toknowifweupdateorcreateleads
                for(toupdate_leads,group_key,group_registrations)inrule_group_info[rule]:
                    iftoupdate_leads:
                        additionnal_description=group_registrations._get_lead_description(_("Newregistrations"),line_counter=True)
                        forleadintoupdate_leads:
                            lead.write({
                                'description':"%s\n%s"%(lead.description,additionnal_description),
                                'registration_ids':[(4,reg.id)forregingroup_registrations],
                            })
                    elifgroup_registrations:
                        lead_vals_list.append(group_registrations._get_lead_values(rule))

        returnself.env['crm.lead'].create(lead_vals_list)

    def_filter_registrations(self,registrations):
        """Keepregistrationsmatchingruleconditions.Thoseare

          *ifafilterisset:filterregistrationsbasedonthisfilter.Thisis
            donelikeasearch,andfilterisadomain;
          *ifacompanyissetontherule,itmustmatchevent'scompany.Note
            thatmulti-companyrulesapplyonevent_lead_rule;
          *ifaneventcategoryitset,itmustmatch;
          *ifaneventisset,itmustmatch;
          *ifbotheventandcategoryareset,oneofthemmustmatch(OR).Ifnone
            ofthoseareset,itisconsideredasOK;

        :paramregistrations:event.registrationrecordsetonwhichrulefilters
          willbeevaluated;
        :return:subsetofregistrationsmatchingrules
        """
        self.ensure_one()
        ifself.event_registration_filterandself.event_registration_filter!='[]':
            registrations=registrations.search(expression.AND([
                [('id','in',registrations.ids)],
                literal_eval(self.event_registration_filter)
            ]))

        #checkfromdirectm2otolinkedm2o/o2mtofilterfirstwithoutinnersearch
        company_ok=lambdaregistration:registration.company_id==self.company_idifself.company_idelseTrue
        event_or_event_type_ok=\
            lambdaregistration:\
                registration.event_id==self.event_idorregistration.event_id.event_type_idinself.event_type_ids\
                if(self.event_idorself.event_type_ids)elseTrue

        returnregistrations.filtered(lambdar:company_ok(r)andevent_or_event_type_ok(r))
