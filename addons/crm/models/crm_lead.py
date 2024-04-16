#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importre
importthreading
fromdatetimeimportdate,datetime,timedelta
frompsycopg2importsql

fromflectraimportapi,fields,models,tools,SUPERUSER_ID
fromflectra.osvimportexpression
fromflectra.tools.translateimport_
fromflectra.toolsimportemail_split
fromflectra.exceptionsimportUserError,AccessError
fromflectra.addons.phone_validation.toolsimportphone_validation
fromcollectionsimportOrderedDict,defaultdict

from.importcrm_stage

_logger=logging.getLogger(__name__)

CRM_LEAD_FIELDS_TO_MERGE=[
    'name',
    'partner_id',
    'campaign_id',
    'company_id',
    'country_id',
    'team_id',
    'state_id',
    'stage_id',
    'medium_id',
    'source_id',
    'user_id',
    'title',
    'city',
    'contact_name',
    'description',
    'mobile',
    'partner_name',
    'phone',
    'probability',
    'expected_revenue',
    'street',
    'street2',
    'zip',
    'create_date',
    'date_action_last',
    'email_from',
    'email_cc',
    'website']

#Subsetofpartnerfields:syncanyofthose
PARTNER_FIELDS_TO_SYNC=[
    'mobile',
    'title',
    'function',
    'website',
]

#Subsetofpartnerfields:syncallornonetoavoidmixedaddresses
PARTNER_ADDRESS_FIELDS_TO_SYNC=[
    'street',
    'street2',
    'city',
    'zip',
    'state_id',
    'country_id',
]

#Thosevalueshavebeendeterminedbasedonbenchmarktominimise
#computationtime,numberoftransactionandtransactiontime.
PLS_COMPUTE_BATCH_STEP=50000 #flectra.models.PREFETCH_MAX=1000butlargerclustercanspeedupglobalcomputation
PLS_UPDATE_BATCH_STEP=5000


classLead(models.Model):
    _name="crm.lead"
    _description="Lead/Opportunity"
    _order="prioritydesc,iddesc"
    _inherit=['mail.thread.cc',
                'mail.thread.blacklist',
                'mail.thread.phone',
                'mail.activity.mixin',
                'utm.mixin',
                'format.address.mixin',
                'phone.validation.mixin']
    _primary_email='email_from'

    #Description
    name=fields.Char(
        'Opportunity',index=True,required=True,
        compute='_compute_name',readonly=False,store=True)
    user_id=fields.Many2one('res.users',string='Salesperson',index=True,tracking=True,default=lambdaself:self.env.user)
    user_email=fields.Char('UserEmail',related='user_id.email',readonly=True)
    user_login=fields.Char('UserLogin',related='user_id.login',readonly=True)
    company_id=fields.Many2one('res.company',string='Company',index=True,default=lambdaself:self.env.company.id)
    referred=fields.Char('ReferredBy')
    description=fields.Text('Notes')
    active=fields.Boolean('Active',default=True,tracking=True)
    type=fields.Selection([
        ('lead','Lead'),('opportunity','Opportunity')],
        index=True,required=True,tracking=15,
        default=lambdaself:'lead'ifself.env['res.users'].has_group('crm.group_use_lead')else'opportunity')
    priority=fields.Selection(
        crm_stage.AVAILABLE_PRIORITIES,string='Priority',index=True,
        default=crm_stage.AVAILABLE_PRIORITIES[0][0])
    team_id=fields.Many2one(
        'crm.team',string='SalesTeam',index=True,tracking=True,
        compute='_compute_team_id',readonly=False,store=True)
    stage_id=fields.Many2one(
        'crm.stage',string='Stage',index=True,tracking=True,
        compute='_compute_stage_id',readonly=False,store=True,
        copy=False,group_expand='_read_group_stage_ids',ondelete='restrict',
        domain="['|',('team_id','=',False),('team_id','=',team_id)]")
    kanban_state=fields.Selection([
        ('grey','Nonextactivityplanned'),
        ('red','Nextactivitylate'),
        ('green','Nextactivityisplanned')],string='KanbanState',
        compute='_compute_kanban_state')
    activity_date_deadline_my=fields.Date(
        'MyActivitiesDeadline',compute='_compute_activity_date_deadline_my',
        search='_search_activity_date_deadline_my',compute_sudo=False,
        readonly=True,store=False,groups="base.group_user")
    tag_ids=fields.Many2many(
        'crm.tag','crm_tag_rel','lead_id','tag_id',string='Tags',
        help="Classifyandanalyzeyourlead/opportunitycategorieslike:Training,Service")
    color=fields.Integer('ColorIndex',default=0)
    #Opportunityspecific
    expected_revenue=fields.Monetary('ExpectedRevenue',currency_field='company_currency',tracking=True)
    prorated_revenue=fields.Monetary('ProratedRevenue',currency_field='company_currency',store=True,compute="_compute_prorated_revenue")
    recurring_revenue=fields.Monetary('RecurringRevenues',currency_field='company_currency',groups="crm.group_use_recurring_revenues")
    recurring_plan=fields.Many2one('crm.recurring.plan',string="RecurringPlan",groups="crm.group_use_recurring_revenues")
    recurring_revenue_monthly=fields.Monetary('ExpectedMRR',currency_field='company_currency',store=True,
                                               compute="_compute_recurring_revenue_monthly",
                                               groups="crm.group_use_recurring_revenues")
    recurring_revenue_monthly_prorated=fields.Monetary('ProratedMRR',currency_field='company_currency',store=True,
                                               compute="_compute_recurring_revenue_monthly_prorated",
                                               groups="crm.group_use_recurring_revenues")
    company_currency=fields.Many2one("res.currency",string='Currency',related='company_id.currency_id',readonly=True)
    #Dates
    date_closed=fields.Datetime('ClosedDate',readonly=True,copy=False)
    date_action_last=fields.Datetime('LastAction',readonly=True)
    date_open=fields.Datetime(
        'AssignmentDate',compute='_compute_date_open',readonly=True,store=True)
    day_open=fields.Float('DaystoAssign',compute='_compute_day_open',store=True)
    day_close=fields.Float('DaystoClose',compute='_compute_day_close',store=True)
    date_last_stage_update=fields.Datetime(
        'LastStageUpdate',compute='_compute_date_last_stage_update',index=True,readonly=True,store=True)
    date_conversion=fields.Datetime('ConversionDate',readonly=True)
    date_deadline=fields.Date('ExpectedClosing',help="Estimateofthedateonwhichtheopportunitywillbewon.")
    #Customer/contact
    partner_id=fields.Many2one(
        'res.partner',string='Customer',index=True,tracking=10,
        domain="['|',('company_id','=',False),('company_id','=',company_id)]",
        help="Linkedpartner(optional).Usuallycreatedwhenconvertingthelead.YoucanfindapartnerbyitsName,TIN,EmailorInternalReference.")
    partner_is_blacklisted=fields.Boolean('Partnerisblacklisted',related='partner_id.is_blacklisted',readonly=True)
    contact_name=fields.Char(
        'ContactName',tracking=30,
        compute='_compute_contact_name',readonly=False,store=True)
    partner_name=fields.Char(
        'CompanyName',tracking=20,index=True,
        compute='_compute_partner_name',readonly=False,store=True,
        help='Thenameofthefuturepartnercompanythatwillbecreatedwhileconvertingtheleadintoopportunity')
    function=fields.Char('JobPosition',compute='_compute_function',readonly=False,store=True)
    title=fields.Many2one('res.partner.title',string='Title',compute='_compute_title',readonly=False,store=True)
    email_from=fields.Char(
        'Email',tracking=40,index=True,
        compute='_compute_email_from',inverse='_inverse_email_from',readonly=False,store=True)
    phone=fields.Char(
        'Phone',tracking=50,
        compute='_compute_phone',inverse='_inverse_phone',readonly=False,store=True)
    mobile=fields.Char('Mobile',compute='_compute_mobile',readonly=False,store=True)
    phone_mobile_search=fields.Char('Phone/Mobile',store=False,search='_search_phone_mobile_search')
    phone_state=fields.Selection([
        ('correct','Correct'),
        ('incorrect','Incorrect')],string='PhoneQuality',compute="_compute_phone_state",store=True)
    email_state=fields.Selection([
        ('correct','Correct'),
        ('incorrect','Incorrect')],string='EmailQuality',compute="_compute_email_state",store=True)
    website=fields.Char('Website',index=True,help="Websiteofthecontact",compute="_compute_website",readonly=False,store=True)
    lang_id=fields.Many2one(
        'res.lang',string='Language',
        compute='_compute_lang_id',readonly=False,store=True)
    #Addressfields
    street=fields.Char('Street',compute='_compute_partner_address_values',readonly=False,store=True)
    street2=fields.Char('Street2',compute='_compute_partner_address_values',readonly=False,store=True)
    zip=fields.Char('Zip',change_default=True,compute='_compute_partner_address_values',readonly=False,store=True)
    city=fields.Char('City',compute='_compute_partner_address_values',readonly=False,store=True)
    state_id=fields.Many2one(
        "res.country.state",string='State',
        compute='_compute_partner_address_values',readonly=False,store=True,
        domain="[('country_id','=?',country_id)]")
    country_id=fields.Many2one(
        'res.country',string='Country',
        compute='_compute_partner_address_values',readonly=False,store=True)
    #Probability(Opportunityonly)
    probability=fields.Float(
        'Probability',group_operator="avg",copy=False,
        compute='_compute_probabilities',readonly=False,store=True)
    automated_probability=fields.Float('AutomatedProbability',compute='_compute_probabilities',readonly=True,store=True)
    is_automated_probability=fields.Boolean('Isautomatedprobability?',compute="_compute_is_automated_probability")
    #Externalrecords
    meeting_count=fields.Integer('#Meetings',compute='_compute_meeting_count')
    lost_reason=fields.Many2one(
        'crm.lost.reason',string='LostReason',
        index=True,ondelete='restrict',tracking=True)
    ribbon_message=fields.Char('Ribbonmessage',compute='_compute_ribbon_message')

    _sql_constraints=[
        ('check_probability','check(probability>=0andprobability<=100)','Theprobabilityofclosingthedealshouldbebetween0%and100%!')
    ]

    @api.depends('activity_date_deadline')
    def_compute_kanban_state(self):
        today=date.today()
        forleadinself:
            kanban_state='grey'
            iflead.activity_date_deadline:
                lead_date=fields.Date.from_string(lead.activity_date_deadline)
                iflead_date>=today:
                    kanban_state='green'
                else:
                    kanban_state='red'
            lead.kanban_state=kanban_state

    @api.depends('activity_ids.date_deadline')
    @api.depends_context('uid')
    def_compute_activity_date_deadline_my(self):
        todo_activities=[]
        ifself.ids:
            todo_activities=self.env['mail.activity'].search([
                ('user_id','=',self._uid),
                ('res_model','=',self._name),
                ('res_id','in',self.ids)
            ],order='date_deadlineASC')

        forrecordinself:
            record.activity_date_deadline_my=next(
                (activity.date_deadlineforactivityintodo_activitiesifactivity.res_id==record.id),
                False
            )

    def_search_activity_date_deadline_my(self,operator,operand):
        return['&',('activity_ids.user_id','=',self._uid),('activity_ids.date_deadline',operator,operand)]

    @api.depends('user_id','type')
    def_compute_team_id(self):
        """Whenchangingtheuser,alsosetateam_idorrestrictteamid
        totheonesuser_idismemberof."""
        forleadinself:
            #settinguserasvoidshouldnottriggeranewteamcomputation
            ifnotlead.user_id:
                continue
            user=lead.user_id
            iflead.team_idanduserinlead.team_id.member_ids|lead.team_id.user_id:
                continue
            team_domain=[('use_leads','=',True)]iflead.type=='lead'else[('use_opportunities','=',True)]
            team=self.env['crm.team']._get_default_team_id(user_id=user.id,domain=team_domain)
            lead.team_id=team.id

    @api.depends('team_id','type')
    def_compute_stage_id(self):
        forleadinself:
            ifnotlead.stage_id:
                lead.stage_id=lead._stage_find(domain=[('fold','=',False)]).id

    @api.depends('user_id')
    def_compute_date_open(self):
        forleadinself:
            lead.date_open=fields.Datetime.now()iflead.user_idelseFalse

    @api.depends('stage_id')
    def_compute_date_last_stage_update(self):
        forleadinself:
            lead.date_last_stage_update=fields.Datetime.now()

    @api.depends('create_date','date_open')
    def_compute_day_open(self):
        """Computedifferencebetweencreatedateandopendate"""
        leads=self.filtered(lambdal:l.date_openandl.create_date)
        others=self-leads
        others.day_open=None
        forleadinleads:
            date_create=fields.Datetime.from_string(lead.create_date).replace(microsecond=0)
            date_open=fields.Datetime.from_string(lead.date_open)
            lead.day_open=abs((date_open-date_create).days)

    @api.depends('create_date','date_closed')
    def_compute_day_close(self):
        """Computedifferencebetweencurrentdateandlogdate"""
        leads=self.filtered(lambdal:l.date_closedandl.create_date)
        others=self-leads
        others.day_close=None
        forleadinleads:
            date_create=fields.Datetime.from_string(lead.create_date)
            date_close=fields.Datetime.from_string(lead.date_closed)
            lead.day_close=abs((date_close-date_create).days)

    @api.depends('partner_id')
    def_compute_name(self):
        forleadinself:
            ifnotlead.nameandlead.partner_idandlead.partner_id.name:
                lead.name=_("%s'sopportunity")%lead.partner_id.name

    @api.depends('partner_id')
    def_compute_contact_name(self):
        """computethenewvalueswhenpartner_idhaschanged"""
        forleadinself:
            lead.update(lead._prepare_contact_name_from_partner(lead.partner_id))

    @api.depends('partner_id')
    def_compute_partner_name(self):
        """computethenewvalueswhenpartner_idhaschanged"""
        forleadinself:
            lead.update(lead._prepare_partner_name_from_partner(lead.partner_id))

    @api.depends('partner_id')
    def_compute_function(self):
        """computethenewvalueswhenpartner_idhaschanged"""
        forleadinself:
            ifnotlead.functionorlead.partner_id.function:
                lead.function=lead.partner_id.function

    @api.depends('partner_id')
    def_compute_title(self):
        """computethenewvalueswhenpartner_idhaschanged"""
        forleadinself:
            ifnotlead.titleorlead.partner_id.title:
                lead.title=lead.partner_id.title

    @api.depends('partner_id')
    def_compute_mobile(self):
        """computethenewvalueswhenpartner_idhaschanged"""
        forleadinself:
            ifnotlead.mobileorlead.partner_id.mobile:
                lead.mobile=lead.partner_id.mobile

    @api.depends('partner_id')
    def_compute_website(self):
        """computethenewvalueswhenpartner_idhaschanged"""
        forleadinself:
            ifnotlead.websiteorlead.partner_id.website:
                lead.website=lead.partner_id.website

    @api.depends('partner_id')
    def_compute_lang_id(self):
        """computethelangbasedonpartnerwhenpartner_idhaschanged"""
        wo_lang=self.filtered(lambdalead:notlead.lang_idandlead.partner_id)
        ifnotwo_lang:
            return
        #preparecache
        lang_codes=[codeforcodeinwo_lang.mapped('partner_id.lang')ifcode]
        lang_id_by_code=dict(
            (code,self.env['res.lang']._lang_get_id(code))
            forcodeinlang_codes
        )
        forleadinwo_lang:
            lead.lang_id=lang_id_by_code.get(lead.partner_id.lang,False)

    @api.depends('partner_id')
    def_compute_partner_address_values(self):
        """Syncallornoneofaddressfields"""
        forleadinself:
            lead.update(lead._prepare_address_values_from_partner(lead.partner_id))

    @api.depends('partner_id.email')
    def_compute_email_from(self):
        forleadinself:
            iflead.partner_id.emailandlead._get_partner_email_update():
                lead.email_from=lead.partner_id.email

    def_inverse_email_from(self):
        forleadinself:
            iflead._get_partner_email_update():
                lead.partner_id.email=lead.email_from

    @api.depends('partner_id.phone')
    def_compute_phone(self):
        forleadinself:
            iflead.partner_id.phoneandlead._get_partner_phone_update():
                lead.phone=lead.partner_id.phone

    def_inverse_phone(self):
        forleadinself:
            iflead._get_partner_phone_update():
                lead.partner_id.phone=lead.phone

    @api.depends('phone','country_id.code')
    def_compute_phone_state(self):
        forleadinself:
            phone_status=False
            iflead.phone:
                country_code=lead.country_id.codeiflead.country_idandlead.country_id.codeelseNone
                try:
                    ifphone_validation.phone_parse(lead.phone,country_code): #otherwiselibrarynotinstalled
                        phone_status='correct'
                exceptUserError:
                    phone_status='incorrect'
            lead.phone_state=phone_status

    @api.depends('email_from')
    def_compute_email_state(self):
        forleadinself:
            email_state=False
            iflead.email_from:
                email_state='incorrect'
                foremailinemail_split(lead.email_from):
                    iftools.email_normalize(email):
                        email_state='correct'
                        break
            lead.email_state=email_state

    @api.depends('probability','automated_probability')
    def_compute_is_automated_probability(self):
        """Ifprobabilityandautomated_probabilityareequalprobabilitycomputation
        isconsideredasautomatic,akaprobabilityissyncwithautomated_probability"""
        forleadinself:
            lead.is_automated_probability=tools.float_compare(lead.probability,lead.automated_probability,2)==0

    @api.depends(lambdaself:['tag_ids','stage_id','team_id']+self._pls_get_safe_fields())
    def_compute_probabilities(self):
        lead_probabilities=self._pls_get_naive_bayes_probabilities()
        forleadinself:
            iflead.idinlead_probabilities:
                was_automated=lead.activeandlead.is_automated_probability
                lead.automated_probability=lead_probabilities[lead.id]
                ifwas_automated:
                    lead.probability=lead.automated_probability

    @api.depends('expected_revenue','probability')
    def_compute_prorated_revenue(self):
        forleadinself:
            lead.prorated_revenue=round((lead.expected_revenueor0.0)*(lead.probabilityor0)/100.0,2)

    @api.depends('recurring_revenue','recurring_plan.number_of_months')
    def_compute_recurring_revenue_monthly(self):
        forleadinself:
            lead.recurring_revenue_monthly=(lead.recurring_revenueor0.0)/(lead.recurring_plan.number_of_monthsor1)

    @api.depends('recurring_revenue_monthly','probability')
    def_compute_recurring_revenue_monthly_prorated(self):
        forleadinself:
            lead.recurring_revenue_monthly_prorated=(lead.recurring_revenue_monthlyor0.0)*(lead.probabilityor0)/100.0

    def_compute_meeting_count(self):
        ifself.ids:
            meeting_data=self.env['calendar.event'].sudo().read_group([
                ('opportunity_id','in',self.ids)
            ],['opportunity_id'],['opportunity_id'])
            mapped_data={m['opportunity_id'][0]:m['opportunity_id_count']forminmeeting_data}
        else:
            mapped_data=dict()
        forleadinself:
            lead.meeting_count=mapped_data.get(lead.id,0)

    @api.depends('email_from','phone','partner_id')
    def_compute_ribbon_message(self):
        forleadinself:
            will_write_email=lead._get_partner_email_update()
            will_write_phone=lead._get_partner_phone_update()

            ifwill_write_emailandwill_write_phone:
                lead.ribbon_message=_('Bysavingthischange,thecustomeremailandphonenumberwillalsobeupdated.')
            elifwill_write_email:
                lead.ribbon_message=_('Bysavingthischange,thecustomeremailwillalsobeupdated.')
            elifwill_write_phone:
                lead.ribbon_message=_('Bysavingthischange,thecustomerphonenumberwillalsobeupdated.')
            else:
                lead.ribbon_message=False

    def_search_phone_mobile_search(self,operator,value):
        value=re.sub(r'[^\d+]+','',value)
        iflen(value)<=2:
            raiseUserError(_('Pleaseenteratleast3digitswhensearchingonphone/mobile.'))

        query=f"""
                SELECTmodel.id
                FROM{self._table}model
                WHEREREGEXP_REPLACE(model.phone,'[^\d+]+','','g')SIMILARTOCONCAT(%s,REGEXP_REPLACE(%s,'\D+','','g'),'%%')
                  ORREGEXP_REPLACE(model.mobile,'[^\d+]+','','g')SIMILARTOCONCAT(%s,REGEXP_REPLACE(%s,'\D+','','g'),'%%')
            """

        #searchingon+32485112233shouldalsofinds00485112233(00/+prefixarebothvalid)
        #wethereforeremoveitfrominputvalueandsearchforbothofthemindb
        ifvalue.startswith('+')orvalue.startswith('00'):
            ifvalue.startswith('00'):
                value=value[2:]
            starts_with='00|\+'
        else:
            starts_with='%'

        self._cr.execute(query,(starts_with,value,starts_with,value))
        res=self._cr.fetchall()
        ifnotres:
            return[(0,'=',1)]
        return[('id','in',[r[0]forrinres])]

    @api.onchange('phone','country_id','company_id')
    def_onchange_phone_validation(self):
        ifself.phone:
            self.phone=self.phone_format(self.phone)

    @api.onchange('mobile','country_id','company_id')
    def_onchange_mobile_validation(self):
        ifself.mobile:
            self.mobile=self.phone_format(self.mobile)

    def_prepare_values_from_partner(self,partner):
        """Getadictionarywithvaluescomingfrompartnerinformationto
        copyonalead.Non-addressfieldsgetthecurrentlead
        valuestoavoidbeingresetifpartnerhasnovalueforthem."""

        #Syncalladdressfieldsfrompartner,ornone,toavoidmixingthem.
        values=self._prepare_address_values_from_partner(partner)

        #Forotherfields,gettheinfofromthepartner,butonlyifset
        values.update({f:partner[f]orself[f]forfinPARTNER_FIELDS_TO_SYNC})
        ifpartner.lang:
            values['lang_id']=self.env['res.lang']._lang_get_id(partner.lang)

        #Fieldswithspecificlogic
        values.update(self._prepare_contact_name_from_partner(partner))
        values.update(self._prepare_partner_name_from_partner(partner))

        returnself._convert_to_write(values)

    def_prepare_address_values_from_partner(self,partner):
        #Syncalladdressfieldsfrompartner,ornone,toavoidmixingthem.
        ifany(partner[f]forfinPARTNER_ADDRESS_FIELDS_TO_SYNC):
            values={f:partner[f]forfinPARTNER_ADDRESS_FIELDS_TO_SYNC}
        else:
            values={f:self[f]forfinPARTNER_ADDRESS_FIELDS_TO_SYNC}
        returnvalues

    def_prepare_contact_name_from_partner(self,partner):
        contact_name=Falseifpartner.is_companyelsepartner.name
        return{'contact_name':contact_nameorself.contact_name}

    def_prepare_partner_name_from_partner(self,partner):
        partner_name=partner.parent_id.name
        ifnotpartner_nameandpartner.is_company:
            partner_name=partner.name
        return{'partner_name':partner_nameorself.partner_name}

    def_get_partner_email_update(self):
        """Calculateifweshouldwritetheemailontherelatedpartner.When
        theemailofthelead/partnerisanemptystring,weforceittoFalse
        tonotpropagateaFalseonanemptystring.

        Doneinaseparatemethodsoitcanbeusedinbothribbonandinverse
        andcomputeofemailupdatemethods.
        """
        self.ensure_one()
        ifself.partner_idandself.email_from!=self.partner_id.email:
            lead_email_normalized=tools.email_normalize(self.email_from)orself.email_fromorFalse
            partner_email_normalized=tools.email_normalize(self.partner_id.email)orself.partner_id.emailorFalse
            returnlead_email_normalized!=partner_email_normalized
        returnFalse

    def_get_partner_phone_update(self):
        """Calculateifweshouldwritethephoneontherelatedpartner.When
        thephoneofthelead/partnerisanemptystring,weforceittoFalse
        tonotpropagateaFalseonanemptystring.

        Doneinaseparatemethodsoitcanbeusedinbothribbonandinverse
        andcomputeofphoneupdatemethods.
        """
        self.ensure_one()
        ifself.partner_idandself.phone!=self.partner_id.phone:
            lead_phone_formatted=self.phone_format(self.phone)ifself.phoneelseFalseorself.phoneorFalse
            partner_phone_formatted=self.phone_format(self.partner_id.phone)ifself.partner_id.phoneelseFalseorself.partner_id.phoneorFalse
            returnlead_phone_formatted!=partner_phone_formatted
        returnFalse

    #------------------------------------------------------------
    #ORM
    #------------------------------------------------------------

    def_auto_init(self):
        res=super(Lead,self)._auto_init()
        tools.create_index(self._cr,'crm_lead_user_id_team_id_type_index',
                           self._table,['user_id','team_id','type'])
        tools.create_index(self._cr,'crm_lead_create_date_team_id_idx',
                           self._table,['create_date','team_id'])
        returnres

    @api.model_create_multi
    defcreate(self,vals_list):
        forvalsinvals_list:
            ifvals.get('website'):
                vals['website']=self.env['res.partner']._clean_website(vals['website'])
        leads=super(Lead,self).create(vals_list)

        forlead,valuesinzip(leads,vals_list):
            ifany(fieldin['active','stage_id']forfieldinvalues):
                lead._handle_won_lost(values)

        returnleads

    defwrite(self,vals):
        ifvals.get('website'):
            vals['website']=self.env['res.partner']._clean_website(vals['website'])

        stage_updated,stage_is_won=vals.get('stage_id'),False
        #stagechange:updatedate_last_stage_update
        ifstage_updated:
            stage=self.env['crm.stage'].browse(vals['stage_id'])
            ifstage.is_won:
                vals.update({'probability':100,'automated_probability':100})
                stage_is_won=True

        #stagechangewithnewstage:updateprobabilityanddate_closed
        ifvals.get('probability',0)>=100ornotvals.get('active',True):
            vals['date_closed']=fields.Datetime.now()
        eliftools.float_compare(vals.get('probability',0),0,precision_digits=2)>0:
            vals['date_closed']=False
        elifstage_updatedandnotstage_is_wonandnot'probability'invals:
            vals['date_closed']=False

        ifany(fieldin['active','stage_id']forfieldinvals):
            self._handle_won_lost(vals)

        ifnotstage_is_won:
            returnsuper(Lead,self).write(vals)

        #stagechangebetweentwowonstages:doesnotchangethedate_closed
        leads_already_won=self.filtered(lambdalead:lead.stage_id.is_won)
        remaining=self-leads_already_won
        ifremaining:
            result=super(Lead,remaining).write(vals)
        ifleads_already_won:
            vals.pop('date_closed',False)
            result=super(Lead,leads_already_won).write(vals)
        returnresult

    @api.model
    defsearch(self,args,offset=0,limit=None,order=None,count=False):
        """Overridetosupportorderingonactivity_date_deadline_my.

        Orderingthroughwebclientcallssearch_readwithanorderparameterset.
        Search_readthencallssearch.Inthisoverridewethereforeoverridesearch
        tointerceptasearchwithoutcountwithanorderonactivity_date_deadline_my.
        Inthatcasewedothesearchintwosteps.

        Firststep:fillwithdeadline-basedresults

          *Performaread_grouponmyactivitiestogetamappinglead_id/deadline
            Rememberdate_deadlineisrequired,wealwayshaveavalueforit.Only
            theearliestdeadlineperleadiskept.
          *Searchleadslinkedtothoseactivitiesthatalsomatchtheaskeddomain
            andorderfromtheoriginalsearchrequest.
          *Resultsofthatsearchwillbeatthetopofreturnedresults.Uselimit
            Nonebecausewehavetosearchallleadslinkedtoactivitiesasordering
            ondeadlineisdoneinpostprocessing.
          *Reorderthemaccordingtodeadlineascordescdependingonoriginal
            searchordering.Finallytakeonlyasubsetofthoseleadstofillwith
            resultsmatchingaskedoffset/limit.

        Secondstep:fillwithotherresults.Iffirststepdoesnotgivesresults
        enoughtomatchoffsetandlimitparameterswefillwithasearchonother
        leads.Wekeeptheaskeddomainandorderingwhilefilteringoutalready
        scannedleadstokeepacoherentresults.

        Allothersearchandsearch_readareleftuntouchedbythisoverridetoavoid
        sideeffects.Search_countisnotaffectedbythisoverride.
        """
        ifcountornotorderor'activity_date_deadline_my'notinorder:
            returnsuper(Lead,self).search(args,offset=offset,limit=limit,order=order,count=count)
        order_items=[order_item.strip().lower()fororder_itemin(orderorself._order).split(',')]

        #Performaread_grouponmyactivitiestogetamappinglead_id/deadline
        #Rememberdate_deadlineisrequired,wealwayshaveavalueforit.Only
        #theearliestdeadlineperleadiskept.
        activity_asc=any('activity_date_deadline_myasc'initemforiteminorder_items)
        my_lead_activities=self.env['mail.activity'].read_group(
            [('res_model','=',self._name),('user_id','=',self.env.uid)],
            ['res_id','date_deadline:min'],
            ['res_id'],
            orderby='date_deadlineASC'
        )
        my_lead_mapping=dict((item['res_id'],item['date_deadline'])foriteminmy_lead_activities)
        my_lead_ids=list(my_lead_mapping.keys())
        my_lead_domain=expression.AND([[('id','in',my_lead_ids)],args])
        my_lead_order=','.join(itemforiteminorder_itemsif'activity_date_deadline_my'notinitem)

        #Searchleadslinkedtothoseactivitiesandorderthem.Seedocstring
        #ofthismethodformoredetails.
        search_res=super(Lead,self).search(my_lead_domain,offset=0,limit=None,order=my_lead_order,count=count)
        my_lead_ids_ordered=sorted(search_res.ids,key=lambdalead_id:my_lead_mapping[lead_id],reverse=notactivity_asc)
        #keeponlyrequestedwindow(offset+limit,oroffset+)
        my_lead_ids_keep=my_lead_ids_ordered[offset:(offset+limit)]iflimitelsemy_lead_ids_ordered[offset:]
        #keeplistofalreadyskippedleadidstoexcludethemfromfuturesearch
        my_lead_ids_skip=my_lead_ids_ordered[:(offset+limit)]iflimitelsemy_lead_ids_ordered

        #donotgofurtheriflimitisachieved
        iflimitandlen(my_lead_ids_keep)>=limit:
            returnself.browse(my_lead_ids_keep)

        #Fillwithremainingleads.Ifalimitisgiven,simplyremovecountof
        #alreadyfetched.Otherwisekeepnone.Ifanoffsetissetwehaveto
        #reduceitbyalreadyfetchresultshereabove.Orderisupdatedtoexclude
        #activity_date_deadline_mywhencallingsuper().
        lead_limit=(limit-len(my_lead_ids_keep))iflimitelseNone
        ifoffset:
            lead_offset=max((offset-len(search_res),0))
        else:
            lead_offset=0
        lead_order=','.join(itemforiteminorder_itemsif'activity_date_deadline_my'notinitem)

        other_lead_res=super(Lead,self).search(
            expression.AND([[('id','notin',my_lead_ids_skip)],args]),
            offset=lead_offset,limit=lead_limit,order=lead_order,count=count
        )
        returnself.browse(my_lead_ids_keep)+other_lead_res

    def_handle_won_lost(self,vals):
        """Thismethodhandlethestatechanges:
        -Tolost:Weneedtoincrementcorrespondinglostcountinscoringfrequencytable
        -Towon:Weneedtoincrementcorrespondingwoncountinscoringfrequencytable
        -FromlosttoWon:Weneedtodecrementcorrespondinglostcount+incrementcorrespondingwoncount
        inscoringfrequencytable.
        -Fromwontolost:Weneedtodecrementcorrespondingwoncount+incrementcorrespondinglostcount
        inscoringfrequencytable."""
        Lead=self.env['crm.lead']
        leads_reach_won=Lead
        leads_leave_won=Lead
        leads_reach_lost=Lead
        leads_leave_lost=Lead
        won_stage_ids=self.env['crm.stage'].search([('is_won','=',True)]).ids
        forleadinself:
            if'stage_id'invals:
                ifvals['stage_id']inwon_stage_ids:
                    iflead.probability==0:
                        leads_leave_lost|=lead
                    leads_reach_won|=lead
                eliflead.stage_id.idinwon_stage_idsandlead.active: #aleadcanbelostatwon_stage
                    leads_leave_won|=lead
            if'active'invals:
                ifnotvals['active']andlead.active: #archivelead
                    iflead.stage_id.idinwon_stage_idsandleadnotinleads_leave_won:
                        leads_leave_won|=lead
                    leads_reach_lost|=lead
                elifvals['active']andnotlead.active: #restorelead
                    leads_leave_lost|=lead

        leads_reach_won._pls_increment_frequencies(to_state='won')
        leads_leave_won._pls_increment_frequencies(from_state='won')
        leads_reach_lost._pls_increment_frequencies(to_state='lost')
        leads_leave_lost._pls_increment_frequencies(from_state='lost')

    @api.returns('self',lambdavalue:value.id)
    defcopy(self,default=None):
        self.ensure_one()
        #setdefaultvalueincontext,ifnotalreadyset(Putstageto'new'stage)
        context=dict(self._context)
        context.setdefault('default_type',self.type)
        context.setdefault('default_team_id',self.team_id.id)
        #Setdate_opentotodayifitisanopp
        default=defaultor{}
        default['date_open']=fields.Datetime.now()ifself.type=='opportunity'elseFalse
        #Donotassigntoanarchiveduser
        ifnotself.user_id.active:
            default['user_id']=False
        ifnotself.env.user.has_group('crm.group_use_recurring_revenues'):
            default['recurring_revenue']=0
            default['recurring_plan']=False
        returnsuper(Lead,self.with_context(context)).copy(default=default)

    defunlink(self):
        """Updatemeetingswhenremovingopportunities,otherwiseyouhave
        alinktoarecordthatdoesnotleadanywhere."""
        meetings=self.env['calendar.event'].search([
            ('res_id','in',self.ids),
            ('res_model','=',self._name),
        ])
        ifmeetings:
            meetings.write({
                'res_id':False,
                'res_model_id':False,
            })
        returnsuper(Lead,self).unlink()

    @api.model
    def_fields_view_get(self,view_id=None,view_type='form',toolbar=False,submenu=False):
        ifself._context.get('opportunity_id'):
            opportunity=self.browse(self._context['opportunity_id'])
            action=opportunity.get_formview_action()
            ifaction.get('views')andany(view_idforview_idinaction['views']ifview_id[1]==view_type):
                view_id=next(view_id[0]forview_idinaction['views']ifview_id[1]==view_type)
        res=super(Lead,self)._fields_view_get(view_id=view_id,view_type=view_type,toolbar=toolbar,submenu=submenu)
        ifview_type=='form':
            res['arch']=self._fields_view_get_address(res['arch'])
        returnres

    @api.model
    def_read_group_stage_ids(self,stages,domain,order):
        #retrieveteam_idfromthecontextandwritethedomain
        #-('id','in',stages.ids):addcolumnsthatshouldbepresent
        #-OR('fold','=',False):adddefaultcolumnsthatarenotfolded
        #-OR('team_ids','=',team_id),('fold','=',False)ifteam_id:addteamcolumnsthatarenotfolded
        team_id=self._context.get('default_team_id')
        ifteam_id:
            search_domain=['|',('id','in',stages.ids),'|',('team_id','=',False),('team_id','=',team_id)]
        else:
            search_domain=['|',('id','in',stages.ids),('team_id','=',False)]

        #performsearch
        stage_ids=stages._search(search_domain,order=order,access_rights_uid=SUPERUSER_ID)
        returnstages.browse(stage_ids)

    def_stage_find(self,team_id=False,domain=None,order='sequence'):
        """Determinethestageofthecurrentleadwithitsteams,thegivendomainandthegiventeam_id
            :paramteam_id
            :paramdomain:basesearchdomainforstage
            :returnscrm.stagerecordset
        """
        #collectallteam_idsbyaddinggivenone,andtheonesrelatedtothecurrentleads
        team_ids=set()
        ifteam_id:
            team_ids.add(team_id)
        forleadinself:
            iflead.team_id:
                team_ids.add(lead.team_id.id)
        #generatethedomain
        ifteam_ids:
            search_domain=['|',('team_id','=',False),('team_id','in',list(team_ids))]
        else:
            search_domain=[('team_id','=',False)]
        #ANDwiththedomaininparameter
        ifdomain:
            search_domain+=list(domain)
        #performsearch,returnthefirstfound
        returnself.env['crm.stage'].search(search_domain,order=order,limit=1)

    #------------------------------------------------------------
    #ACTIONS
    #------------------------------------------------------------

    deftoggle_active(self):
        """Whenarchiving:markprobabilityas0.Whenre-activating
        updateprobabilityagain,forleadsandopportunities."""
        res=super(Lead,self).toggle_active()
        activated=self.filtered(lambdalead:lead.active)
        archived=self.filtered(lambdalead:notlead.active)
        ifactivated:
            activated.write({'lost_reason':False})
            activated._compute_probabilities()
        ifarchived:
            archived.write({'probability':0,'automated_probability':0})
        returnres

    defaction_set_lost(self,**additional_values):
        """Lostsemantic:probability=0oractive=False"""
        res=self.action_archive()
        ifadditional_values:
            self.write(dict(additional_values))
        returnres

    defaction_set_won(self):
        """Wonsemantic:probability=100(activeuntouched)"""
        self.action_unarchive()
        #grouptheleadsbyteam_id,inordertowriteoncebyvaluescouple(eachwriteleadstofrequencyincrement)
        leads_by_won_stage={}
        forleadinself:
            stage_id=lead._stage_find(domain=[('is_won','=',True)])
            ifstage_idinleads_by_won_stage:
                leads_by_won_stage[stage_id]|=lead
            else:
                leads_by_won_stage[stage_id]=lead
        forwon_stage_id,leadsinleads_by_won_stage.items():
            leads.write({'stage_id':won_stage_id.id,'probability':100})
        returnTrue

    defaction_set_automated_probability(self):
        self.write({'probability':self.automated_probability})

    defaction_set_won_rainbowman(self):
        self.ensure_one()
        self.action_set_won()

        message=self._get_rainbowman_message()
        ifmessage:
            return{
                'effect':{
                    'fadeout':'slow',
                    'message':message,
                    'img_url':'/web/image/%s/%s/image_1024'%(self.team_id.user_id._name,self.team_id.user_id.id)ifself.team_id.user_id.image_1024else'/web/static/src/img/smile.svg',
                    'type':'rainbow_man',
                }
            }
        returnTrue

    defget_rainbowman_message(self):
        self.ensure_one()
        ifself.stage_id.is_won:
            returnself._get_rainbowman_message()
        returnFalse

    def_get_rainbowman_message(self):
        message=False
        ifself.user_idandself.team_idandself.expected_revenue:
            self.flush() #flushfieldstomakesureDBisuptodate
            query="""
                SELECT
                    SUM(CASEWHENuser_id=%(user_id)sTHEN1ELSE0END)astotal_won,
                    MAX(CASEWHENdate_closed>=CURRENT_DATE-INTERVAL'30days'ANDuser_id=%(user_id)sTHENexpected_revenueELSE0END)asmax_user_30,
                    MAX(CASEWHENdate_closed>=CURRENT_DATE-INTERVAL'7days'ANDuser_id=%(user_id)sTHENexpected_revenueELSE0END)asmax_user_7,
                    MAX(CASEWHENdate_closed>=CURRENT_DATE-INTERVAL'30days'ANDteam_id=%(team_id)sTHENexpected_revenueELSE0END)asmax_team_30,
                    MAX(CASEWHENdate_closed>=CURRENT_DATE-INTERVAL'7days'ANDteam_id=%(team_id)sTHENexpected_revenueELSE0END)asmax_team_7
                FROMcrm_lead
                WHERE
                    type='opportunity'
                AND
                    active=True
                AND
                    probability=100
                AND
                    DATE_TRUNC('year',date_closed)=DATE_TRUNC('year',CURRENT_DATE)
                AND
                    (user_id=%(user_id)sORteam_id=%(team_id)s)
            """
            self.env.cr.execute(query,{'user_id':self.user_id.id,
                                        'team_id':self.team_id.id})
            query_result=self.env.cr.dictfetchone()

            ifquery_result['total_won']==1:
                message=_('Go,go,go!Congratsforyourfirstdeal.')
            elifquery_result['max_team_30']==self.expected_revenue:
                message=_('Boom!Teamrecordforthepast30days.')
            elifquery_result['max_team_7']==self.expected_revenue:
                message=_('Yeah!Dealofthelast7daysfortheteam.')
            elifquery_result['max_user_30']==self.expected_revenue:
                message=_('Youjustbeatyourpersonalrecordforthepast30days.')
            elifquery_result['max_user_7']==self.expected_revenue:
                message=_('Youjustbeatyourpersonalrecordforthepast7days.')
        returnmessage

    defaction_schedule_meeting(self):
        """Openmeeting'scalendarviewtoschedulemeetingoncurrentopportunity.
            :returndict:dictionaryvalueforcreatedMeetingview
        """
        self.ensure_one()
        action=self.env["ir.actions.actions"]._for_xml_id("calendar.action_calendar_event")
        partner_ids=self.env.user.partner_id.ids
        ifself.partner_id:
            partner_ids.append(self.partner_id.id)
        current_opportunity_id=self.idifself.type=='opportunity'elseFalse
        action['context']={
            'search_default_opportunity_id':current_opportunity_id,
            'default_opportunity_id':current_opportunity_id,
            'default_partner_id':self.partner_id.id,
            'default_partner_ids':partner_ids,
            'default_attendee_ids':[(0,0,{'partner_id':pid})forpidinpartner_ids],
            'default_team_id':self.team_id.id,
            'default_name':self.name,
        }
        returnaction

    defaction_snooze(self):
        self.ensure_one()
        today=date.today()
        my_next_activity=self.activity_ids.filtered(lambdaactivity:activity.user_id==self.env.user)[:1]
        ifmy_next_activity:
            ifmy_next_activity.date_deadline<today:
                date_deadline=today+timedelta(days=7)
            else:
                date_deadline=my_next_activity.date_deadline+timedelta(days=7)
            my_next_activity.write({
                'date_deadline':date_deadline
            })
        returnTrue

    #------------------------------------------------------------
    #BUSINESS
    #------------------------------------------------------------

    deflog_meeting(self,meeting_subject,meeting_date,duration):
        ifnotduration:
            duration=_('unknown')
        else:
            duration=str(duration)
        meet_date=fields.Datetime.from_string(meeting_date)
        meeting_usertime=fields.Datetime.to_string(fields.Datetime.context_timestamp(self,meet_date))
        html_time="<timedatetime='%s+00:00'>%s</time>"%(meeting_date,meeting_usertime)
        message=_("Meetingscheduledat'%s'<br>Subject:%s<br>Duration:%shours")%(html_time,meeting_subject,duration)
        returnself.message_post(body=message)

    #------------------------------------------------------------
    #MERGELEADS/OPPS
    #------------------------------------------------------------

    def_merge_get_result_type(self):
        """Definethetypeoftheresultofthemerge. Ifatleastoneofthe
        elementtomergeisanopp,theresultingnewelementwillbeanopp.
        Otherwiseitwillbealead."""
        ifany(record.type=='opportunity'forrecordinself):
            return'opportunity'
        return'lead'

    def_merge_data(self,fields):
        """Preparelead/oppdataintoadictionaryformerging.Differenttypes
            offieldsareprocessedindifferentways:
                -text:allthevaluesareconcatenated
                -m2mando2m:thosefieldsaren'tprocessed
                -m2o:thefirstnotnullvalueprevails(theotheraredropped)
                -anyothertypeoffield:sameasm2o

            :paramfields:listoffieldstoprocess
            :returndictdata:containsthemergedvaluesofthenewopportunity
        """
        #helpers
        def_get_first_not_null(attr,opportunities):
            foroppinopportunities:
                val=opp[attr]
                ifval:
                    returnval
            returnFalse

        def_get_first_not_null_id(attr,opportunities):
            res=_get_first_not_null(attr,opportunities)
            returnres.idifreselseFalse

        #processthefields'values
        data={}
        forfield_nameinfields:
            field=self._fields.get(field_name)
            iffieldisNone:
                continue
            iffield.typein('many2many','one2many'):
                continue
            eliffield.type=='many2one':
                data[field_name]=_get_first_not_null_id(field_name,self) #takethefirstnotnull
            eliffield.type=='text':
                data[field_name]='\n\n'.join(itforitinself.mapped(field_name)ifit)
            else:
                data[field_name]=_get_first_not_null(field_name,self)

        #definetheresultingtype('lead'or'opportunity')
        data['type']=self._merge_get_result_type()
        returndata

    def_merge_notify_get_merged_fields_message(self,fields):
        """Generatethemessagebodywiththechangedvalues

        :paramfields:listoffieldstotrack
        :returnsalistofmessagebodiesforthecorrespondingleads
        """
        bodies=[]
        forleadinself:
            title="%s:%s\n"%(_('Mergedopportunity')iflead.type=='opportunity'else_('Mergedlead'),lead.name)
            body=[title]
            _fields=self.env['ir.model.fields'].search([
                ('name','in',fieldsor[]),
                ('model_id.model','=',lead._name),
            ])
            forfieldin_fields:
                value=getattr(lead,field.name,False)
                iffield.ttype=='selection':
                    selections=lead.fields_get()[field.name]['selection']
                    value=next((v[1]forvinselectionsifv[0]==value),value)
                eliffield.ttype=='many2one':
                    ifvalue:
                        value=value.sudo().display_name
                eliffield.ttype=='many2many':
                    ifvalue:
                        value=','.join(
                            val.display_name
                            forvalinvalue.sudo()
                        )
                body.append("%s:%s"%(field.field_description,valueor''))
            bodies.append("<br/>".join(body+['<br/>']))
        returnbodies

    def_merge_notify(self,opportunities):
        """Postamessagegatheringmergedleads/oppsinformations.Itexplains
        whichfieldshasbeenmergedandtheirnewvalue.`self`istheresulting
        mergecrm.leadrecord.

        :paramopportunities:see``merge_dependences``
        """
        #TODOJEM:mailtemplateshouldbeusedinsteadoffixbody,subjecttext
        self.ensure_one()
        #mailmessage'ssubject
        result_type=opportunities._merge_get_result_type()
        merge_message=_('Mergedleads')ifresult_type=='lead'else_('Mergedopportunities')
        subject=merge_message+":"+",".join(opportunities.mapped('name'))
        #messagebodies
        message_bodies=opportunities._merge_notify_get_merged_fields_message(list(CRM_LEAD_FIELDS_TO_MERGE))
        message_body="\n\n".join(message_bodies)
        returnself.message_post(body=message_body,subject=subject)

    def_merge_opportunity_history(self,opportunities):
        """Movemail.messagefromthegivenopportunitiestothecurrentone.`self`isthe
            crm.leadrecorddestinationformessageof`opportunities`.

        :paramopportunities:see``merge_dependences``
        """
        self.ensure_one()
        foropportunityinopportunities:
            formessageinopportunity.message_ids:
                ifmessage.subject:
                    subject=_("From%(source_name)s:%(source_subject)s",source_name=opportunity.name,source_subject=message.subject)
                else:
                    subject=_("From%(source_name)s",source_name=opportunity.name)
                message.write({
                    'res_id':self.id,
                    'subject':subject,
                })
        returnTrue

    def_merge_opportunity_attachments(self,opportunities):
        """Moveattachmentsofgivenopportunitiestothecurrentone`self`,andrename
            theattachmentshavingsamenamethannativeones.

        :paramopportunities:see``merge_dependences``
        """
        self.ensure_one()

        #returnattachmentsofopportunity
        def_get_attachments(opportunity_id):
            returnself.env['ir.attachment'].search([('res_model','=',self._name),('res_id','=',opportunity_id)])

        first_attachments=_get_attachments(self.id)
        #counterofallattachmentstomove.Usedtomakesurethenameisdifferentforallattachments
        count=1
        foropportunityinopportunities:
            attachments=_get_attachments(opportunity.id)
            forattachmentinattachments:
                values={'res_id':self.id}
                forattachment_in_firstinfirst_attachments:
                    ifattachment.name==attachment_in_first.name:
                        values['name']="%s(%s)"%(attachment.name,count)
                count+=1
                attachment.write(values)
        returnTrue

    defmerge_dependences(self,opportunities):
        """Mergedependences(messages,attachments,...).Thesedependenceswillbe
            transferedto`self`,themostimportantlead.

        :paramopportunities:recordsetofopportunitiestotransfer.Doesnot
          include`self`whichisthetargetcrm.leadbeingtheresultofthemerge.
        """
        self.ensure_one()
        self._merge_notify(opportunities)
        self._merge_opportunity_history(opportunities)
        self._merge_opportunity_attachments(opportunities)

    defmerge_opportunity(self,user_id=False,team_id=False,auto_unlink=True):
        """Mergeopportunitiesinone.Differentcasesofmerge:
                -mergeleadstogether=1newlead
                -mergeatleast1oppwithanythingelse(leadoropp)=1newopp
            Theresultinglead/opportunitywillbethemostimportantone(basedonitsconfidencelevel)
            updatedwithvaluesfromotheropportunitiestomerge.
            :paramuser_id:theidofthesaleperson.Ifnotgiven,willbedeterminedby`_merge_data`.
            :paramteam:theidoftheSalesTeam.Ifnotgiven,willbedeterminedby`_merge_data`.
            :returncrm.leadrecordresultingofthmerge
        """
        iflen(self.ids)<=1:
            raiseUserError(_('Pleaseselectmorethanoneelement(leadoropportunity)fromthelistview.'))

        iflen(self.ids)>5andnotself.env.is_superuser():
            raiseUserError(_("Topreventdataloss,LeadsandOpportunitiescanonlybemergedbygroupsof5."))

        opportunities=self._sort_by_confidence_level(reverse=True)

        #getSORTEDrecordsetofheadandtail,andcompletelist
        opportunities_head=opportunities[0]
        opportunities_tail=opportunities[1:]

        #mergeallthesortedopportunity.Thismeansthevalueof
        #thefirst(headopp)willbeapriority.
        merged_data=opportunities._merge_data(list(CRM_LEAD_FIELDS_TO_MERGE))

        #forcevalueforsalepersonandSalesTeam
        ifuser_id:
            merged_data['user_id']=user_id
        ifteam_id:
            merged_data['team_id']=team_id

        #mergeotherdata(mail.message,attachments,...)fromtailintohead
        opportunities_head.merge_dependences(opportunities_tail)

        #checkifthestageisinthestagesoftheSalesTeam.Ifnot,assignthestagewiththelowestsequence
        ifmerged_data.get('team_id'):
            team_stage_ids=self.env['crm.stage'].search(['|',('team_id','=',merged_data['team_id']),('team_id','=',False)],order='sequence')
            ifmerged_data.get('stage_id')notinteam_stage_ids.ids:
                merged_data['stage_id']=team_stage_ids[0].idifteam_stage_idselseFalse

        #writemergeddataintofirstopportunity
        opportunities_head.write(merged_data)

        #deletetailopportunities
        #weusetheSUPERUSERtoavoidaccessrightsissuesbecauseastheuserhadtherightstoseetherecordsitshouldbesafetodoso
        ifauto_unlink:
            opportunities_tail.sudo().unlink()

        returnopportunities_head

    def_sort_by_confidence_level(self,reverse=False):
        """Sortingtheleads/oppsaccordingtotheconfidencelevelofitsstage,whichrelatestotheprobabilityofwinningit
        Theconfidencelevelincreaseswiththestagesequence
        AnOpportunityalwayshashigherconfidencelevelthanalead
        """
        defopps_key(opportunity):
            returnopportunity.type=='opportunity',opportunity.stage_id.sequence,-opportunity._origin.id

        returnself.sorted(key=opps_key,reverse=reverse)

    def_convert_opportunity_data(self,customer,team_id=False):
        """Extractthedatafromaleadtocreatetheopportunity
            :paramcustomer:res.partnerrecord
            :paramteam_id:identifieroftheSalesTeamtodeterminethestage
        """
        new_team_id=team_idifteam_idelseself.team_id.id
        upd_values={
            'type':'opportunity',
            'date_open':fields.Datetime.now(),
            'date_conversion':fields.Datetime.now(),
        }
        ifcustomer!=self.partner_id:
            upd_values['partner_id']=customer.idifcustomerelseFalse
        ifnotself.stage_id:
            stage=self._stage_find(team_id=new_team_id)
            upd_values['stage_id']=stage.id
        returnupd_values

    defconvert_opportunity(self,partner_id,user_ids=False,team_id=False):
        customer=False
        ifpartner_id:
            customer=self.env['res.partner'].browse(partner_id)
        forleadinself:
            ifnotlead.activeorlead.probability==100:
                continue
            vals=lead._convert_opportunity_data(customer,team_id)
            lead.write(vals)

        ifuser_idsorteam_id:
            self.handle_salesmen_assignment(user_ids,team_id)

        returnTrue

    def_get_lead_duplicates(self,partner=None,email=None,include_lost=False):
        """Searchforleadsthatseemduplicatedbasedonpartner/email.

        :parampartner:optionalcustomerwhensearchingduplicated
        :paramemail:email(possiblyformatted)tosearch
        :parambooleaninclude_lost:ifTrue,searchincludesarchivedopportunities
          (stillonlyactiveleadsareconsidered).IfFalse,searchforactive
          andnotwonleadsandopportunities;
        """
        ifnotemailandnotpartner:
            returnself.env['crm.lead']

        domain=[]
        fornormalized_emailin[tools.email_normalize(email)foremailintools.email_split(email)]:
            domain.append(('email_normalized','=',normalized_email))
        ifpartner:
            domain.append(('partner_id','=',partner.id))

        ifnotdomain:
            returnself.env['crm.lead']

        domain=['|']*(len(domain)-1)+domain
        ifinclude_lost:
            domain+=['|',('type','=','opportunity'),('active','=',True)]
        else:
            domain+=['&',('active','=',True),'|',('probability','=',False),('probability','<',100)]

        returnself.with_context(active_test=False).search(domain)

    def_create_customer(self):
        """Createapartnerfromleaddataandlinkittothelead.

        :return:newly-createdpartnerbrowserecord
        """
        Partner=self.env['res.partner']
        contact_name=self.contact_name
        ifnotcontact_name:
            contact_name=Partner._parse_partner_name(self.email_from)[0]ifself.email_fromelseFalse

        ifself.partner_name:
            partner_company=Partner.create(self._prepare_customer_values(self.partner_name,is_company=True))
        elifself.partner_id:
            partner_company=self.partner_id
        else:
            partner_company=None

        ifcontact_name:
            returnPartner.create(self._prepare_customer_values(contact_name,is_company=False,parent_id=partner_company.idifpartner_companyelseFalse))

        ifpartner_company:
            returnpartner_company
        returnPartner.create(self._prepare_customer_values(self.name,is_company=False))

    def_prepare_customer_values(self,partner_name,is_company=False,parent_id=False):
        """Extractdatafromleadtocreateapartner.

        :paramname:furturnameofthepartner
        :paramis_company:Trueifthepartnerisacompany
        :paramparent_id:idoftheparentpartner(Falseifnoparent)

        :return:dictionaryofvaluestogiveatres_partner.create()
        """
        email_split=tools.email_split(self.email_from)
        res={
            'name':partner_name,
            'user_id':self.env.context.get('default_user_id')orself.user_id.id,
            'comment':self.description,
            'team_id':self.team_id.id,
            'parent_id':parent_id,
            'phone':self.phone,
            'mobile':self.mobile,
            'email':email_split[0]ifemail_splitelseFalse,
            'title':self.title.id,
            'function':self.function,
            'street':self.street,
            'street2':self.street2,
            'zip':self.zip,
            'city':self.city,
            'country_id':self.country_id.id,
            'state_id':self.state_id.id,
            'website':self.website,
            'is_company':is_company,
            'type':'contact'
        }
        ifself.lang_id:
            res['lang']=self.lang_id.code
        returnres

    def_find_matching_partner(self,email_only=False):
        """Trytofindamatchingpartnerwithavailableinformationonthe
        lead,usingnotablycustomer'sname,email,...

        :paramemail_only:Onlyfindamatchingbasedontheemail.Touse
            forautomaticprocesswhereilikebasedonnamecanbetoodangerous
        :return:partnerbrowserecord
        """
        self.ensure_one()
        partner=self.partner_id

        ifnotpartnerandself.email_from:
            partner=self.env['res.partner'].search([('email','=',self.email_from)],limit=1)

        ifnotpartnerandnotemail_only:
            #searchthroughtheexistingpartnersbasedonthelead'spartnerorcontactname
            #tobealignedwith_create_customer,searchonlead'snameaslastpossibility
            forcustomer_potential_namein[self[field_name]forfield_namein['partner_name','contact_name','name']ifself[field_name]]:
                partner=self.env['res.partner'].search([('name','ilike','%'+customer_potential_name+'%')],limit=1)
                ifpartner:
                    break

        returnpartner

    defhandle_partner_assignment(self,force_partner_id=False,create_missing=True):
        """Updatecustomer(partner_id)ofleads.Purposeistosetthesame
        partneronmostleads;eitherthroughanewlycreatedpartnereither
        throughagivenpartner_id.

        :paramintforce_partner_id:ifset,updateallleadstothatcustomer;
        :paramcreate_missing:forleadswithoutcustomer,createanewone
          basedonleadinformation;
        """
        forleadinself:
            ifforce_partner_id:
                lead.partner_id=force_partner_id
            ifnotlead.partner_idandcreate_missing:
                partner=lead._create_customer()
                lead.partner_id=partner.id

    defhandle_salesmen_assignment(self,user_ids=None,team_id=False):
        """Assignsalesmenandsalesteamtoabatchofleads. Iftherearemore
        leadsthansalesmen,thesesalesmenwillbeassignedinround-robin.E.g.
        4salesmen(S1,S2,S3,S4)for6leads(L1,L2,...L6)willassignedas
        following:L1-S1,L2-S2,L3-S3,L4-S4,L5-S1,L6-S2.

        :paramlistuser_ids:salesmentoassign
        :paramintteam_id:salesteamtoassign
        """
        update_vals={'team_id':team_id}ifteam_idelse{}
        ifnotuser_ids:
            self.write(update_vals)
        else:
            lead_ids=self.ids
            steps=len(user_ids)
            #pass1:lead_ids[0:6:3]=[L1,L4]
            #pass2:lead_ids[1:6:3]=[L2,L5]
            #pass3:lead_ids[2:6:3]=[L3,L6]
            #...
            foridxinrange(0,steps):
                subset_ids=lead_ids[idx:len(lead_ids):steps]
                update_vals['user_id']=user_ids[idx]
                self.env['crm.lead'].browse(subset_ids).write(update_vals)

    #------------------------------------------------------------
    #TOOLS
    #------------------------------------------------------------

    defredirect_lead_opportunity_view(self):
        self.ensure_one()
        return{
            'name':_('LeadorOpportunity'),
            'view_mode':'form',
            'res_model':'crm.lead',
            'domain':[('type','=',self.type)],
            'res_id':self.id,
            'view_id':False,
            'type':'ir.actions.act_window',
            'context':{'default_type':self.type}
        }

    @api.model
    defget_empty_list_help(self,help):
        help_title,sub_title="",""
        ifself._context.get('default_type')=='lead':
            help_title=_('Createanewlead')
        else:
            help_title=_('Createanopportunitytostartplayingwithyourpipeline.')
        alias_record=self.env['mail.alias'].search([
            ('alias_name','!=',False),
            ('alias_name','!=',''),
            ('alias_model_id.model','=','crm.lead'),
            ('alias_parent_model_id.model','=','crm.team'),
            ('alias_force_thread_id','=',False)
        ],limit=1)
        ifalias_recordandalias_record.alias_domainandalias_record.alias_name:
            email='%s@%s'%(alias_record.alias_name,alias_record.alias_domain)
            email_link="<b><ahref='mailto:%s'>%s</a></b>"%(email,email)
            sub_title=_('Usethetopleft<i>Create</i>button,orsendanemailto%stotesttheemailgateway.')%(email_link)
        return'<pclass="o_view_nocontent_smiling_face">%s</p><pclass="oe_view_nocontent_alias">%s</p>'%(help_title,sub_title)

    #------------------------------------------------------------
    #MAILING
    #------------------------------------------------------------

    def_creation_subtype(self):
        returnself.env.ref('crm.mt_lead_create')

    def_track_subtype(self,init_values):
        self.ensure_one()
        if'stage_id'ininit_valuesandself.probability==100andself.stage_id:
            returnself.env.ref('crm.mt_lead_won')
        elif'lost_reason'ininit_valuesandself.lost_reason:
            returnself.env.ref('crm.mt_lead_lost')
        elif'stage_id'ininit_values:
            returnself.env.ref('crm.mt_lead_stage')
        elif'active'ininit_valuesandself.active:
            returnself.env.ref('crm.mt_lead_restored')
        elif'active'ininit_valuesandnotself.active:
            returnself.env.ref('crm.mt_lead_lost')
        returnsuper(Lead,self)._track_subtype(init_values)

    def_notify_get_groups(self,msg_vals=None):
        """Handlesalesmanrecipientsthatcanconvertleadsintoopportunities
        andsetopportunitiesaswon/lost."""
        groups=super(Lead,self)._notify_get_groups(msg_vals=msg_vals)
        local_msg_vals=dict(msg_valsor{})

        self.ensure_one()
        ifself.type=='lead':
            convert_action=self._notify_get_action_link('controller',controller='/lead/convert',**local_msg_vals)
            salesman_actions=[{'url':convert_action,'title':_('Converttoopportunity')}]
        else:
            won_action=self._notify_get_action_link('controller',controller='/lead/case_mark_won',**local_msg_vals)
            lost_action=self._notify_get_action_link('controller',controller='/lead/case_mark_lost',**local_msg_vals)
            salesman_actions=[
                {'url':won_action,'title':_('Won')},
                {'url':lost_action,'title':_('Lost')}]

        ifself.team_id:
            custom_params=dict(local_msg_vals,res_id=self.team_id.id,model=self.team_id._name)
            salesman_actions.append({
                'url':self._notify_get_action_link('view',**custom_params),
                'title':_('SalesTeamSettings')
            })

        salesman_group_id=self.env.ref('sales_team.group_sale_salesman').id
        new_group=(
            'group_sale_salesman',lambdapdata:pdata['type']=='user'andsalesman_group_idinpdata['groups'],{
                'actions':salesman_actions,
            })

        return[new_group]+groups

    def_notify_get_reply_to(self,default=None,records=None,company=None,doc_names=None):
        """Overridetosetaliasofleadandopportunitiestotheirsalesteamifany."""
        aliases=self.mapped('team_id').sudo()._notify_get_reply_to(default=default,records=None,company=company,doc_names=None)
        res={lead.id:aliases.get(lead.team_id.id)forleadinself}
        leftover=self.filtered(lambdarec:notrec.team_id)
        ifleftover:
            res.update(super(Lead,leftover)._notify_get_reply_to(default=default,records=None,company=company,doc_names=doc_names))
        returnres

    def_message_get_default_recipients(self):
        return{
            r.id:{
                'partner_ids':[],
                'email_to':','.join(tools.email_normalize_all(r.email_from))orr.email_from,
                'email_cc':False,
            }forrinself
        }

    def_message_get_suggested_recipients(self):
        recipients=super(Lead,self)._message_get_suggested_recipients()
        try:
            forleadinself:
                iflead.partner_id:
                    lead._message_add_suggested_recipient(recipients,partner=lead.partner_id,reason=_('Customer'))
                eliflead.email_from:
                    lead._message_add_suggested_recipient(recipients,email=lead.email_from,reason=_('CustomerEmail'))
        exceptAccessError: #noreadaccessrights->justignoresuggestedrecipientsbecausethisimplymodifyingfollowers
            pass
        returnrecipients

    @api.model
    defmessage_new(self,msg_dict,custom_values=None):
        """Overridesmail_threadmessage_newthatiscalledbythemailgateway
            throughmessage_process.
            Thisoverrideupdatesthedocumentaccordingtotheemail.
        """

        #removeexternalusers
        ifself.env.user.has_group('base.group_portal'):
            self=self.with_context(default_user_id=False)

        #removedefaultauthorwhengoingthroughthemailgateway.Indeedwe
        #donotwanttoexplicitlysetuser_idtoFalse;howeverwedonot
        #wantthegatewayusertoberesponsibleifnootherresponsibleis
        #found.
        ifself._uid==self.env.ref('base.user_root').id:
            self=self.with_context(default_user_id=False)

        ifcustom_valuesisNone:
            custom_values={}
        defaults={
            'name': msg_dict.get('subject')or_("NoSubject"),
            'email_from':msg_dict.get('from'),
            'partner_id':msg_dict.get('author_id',False),
        }
        ifmsg_dict.get('priority')indict(crm_stage.AVAILABLE_PRIORITIES):
            defaults['priority']=msg_dict.get('priority')
        defaults.update(custom_values)

        #assignrightcompany
        if'company_id'notindefaultsand'team_id'indefaults:
            defaults['company_id']=self.env['crm.team'].browse(defaults['team_id']).company_id.id
        returnsuper(Lead,self).message_new(msg_dict,custom_values=defaults)

    def_message_post_after_hook(self,message,msg_vals):
        ifself.email_fromandnotself.partner_id:
            #weconsiderthatpostingamessagewithaspecifiedrecipient(notafollower,aspecificone)
            #onadocumentwithoutcustomermeansthatitwascreatedthroughthechatterusing
            #suggestedrecipients.ThisheuristicallowstoavoiduglyhacksinJS.
            new_partner=message.partner_ids.filtered(
                lambdapartner:partner.email==self.email_fromor(self.email_normalizedandpartner.email_normalized==self.email_normalized)
            )
            ifnew_partner:
                ifnew_partner[0].email_normalized:
                    email_domain=('email_normalized','=',new_partner[0].email_normalized)
                else:
                    email_domain=('email_from','=',new_partner[0].email)
                self.search([
                    ('partner_id','=',False),email_domain,('stage_id.fold','=',False)
                ]).write({'partner_id':new_partner[0].id})
        returnsuper(Lead,self)._message_post_after_hook(message,msg_vals)

    def_message_partner_info_from_emails(self,emails,link_mail=False):
        """Trytoproposeabetterrecipientwhenhavingonlyanemailbypopulating
        itwiththepartner_name/contact_namefieldoftheleade.g.iflead
        contact_nameis"Raoul"andemailis"raoul@raoul.fr",suggest
        "Raoul"<raoul@raoul.fr>asrecipient."""
        result=super(Lead,self)._message_partner_info_from_emails(emails,link_mail=link_mail)
        foremail,partner_infoinzip(emails,result):
            ifpartner_info.get('partner_id')ornotemailornot(self.partner_nameorself.contact_name):
                continue
            #reformatemailifnonameinformation
            name_emails=tools.email_split_tuples(email)
            name_from_email=name_emails[0][0]ifname_emailselseFalse
            ifname_from_email:
                continue #alreadycontainingname+email
            name_from_email=self.partner_nameorself.contact_name
            emails_normalized=tools.email_normalize_all(email)
            email_normalized=emails_normalized[0]ifemails_normalizedelseFalse
            ifemail.lower()==self.email_from.lower()or(email_normalizedandself.email_normalized==email_normalized):
                partner_info['full_name']=tools.formataddr((
                    name_from_email,
                    ','.join(emails_normalized)ifemails_normalizedelseemail))
                break
        returnresult

    def_phone_get_number_fields(self):
        """Usemobileorphonefieldstocomputesanitizedphonenumber"""
        return['mobile','phone']

    @api.model
    defget_import_templates(self):
        return[{
            'label':_('ImportTemplateforLeads&Opportunities'),
            'template':'/crm/static/xls/crm_lead.xls'
        }]

    #------------------------------------------------------------
    #PLS
    #------------------------------------------------------------
    #Predictiveleadscoringiscomputingtheleadprobability,basedonwonandlostleadsfromthepast
    #Eachwon/lostleadincrementsafrequencytable,wherewestore,foreachfield/valuecouple,thenumberof
    #wonandlostleads.
    #  E.g.:AwonleadfromBelgiumwillincreasethewoncountofthefrequencycountry_id='Belgium'by1.
    #Thefrequenciesaresplitbyteam_id,soeachteamhashisownfrequenciesenvironment.(TeamAdoesn'timpactB)
    #Therearetwomainwaystobuildthefrequencytable:
    #  -LiveIncrement:AteachWon/lost,weincrementdirectlythefrequenciesbasedontheleadvalues.
    #      DonerightBEFOREwritingtheleadaswonorlost.
    #      Weconsideraleadthatwillbemarkedaswonorlost.
    #      Usedeachtimealeadiswonorlost,toensurefrequencytableisalwaysuptodate
    #  -OneshotRebuild:emptythefrequencytableandrebuilditfromscratch,basedoneveryalreadywon/lostleads
    #      Doneduringcronprocess.
    #      Weconsideralltheleadsthathavebeenalreadywonorlost.
    #      Usedinoneshot,whenmodifyingthecriteriatotakeintoaccount(fieldsorreferencedate)

    #---------------------------------
    #PLS:ProbabilityComputation
    #---------------------------------
    def_pls_get_naive_bayes_probabilities(self,batch_mode=False):
        """
        Inmachinelearning,naiveBayesclassifiers(NBC)areafamilyofsimple"probabilisticclassifiers"basedon
        applyingBayestheoremwithstrong(naive)independenceassumptionsbetweenthevariablestakenintoaccount.
        E.g:willTDEeatm&m'sdependingonhissleepstatus,theamountofworkhehasandthefullnessofhisstomach?
        Asweuseexperiencetocomputethestatistics,everyday,wewillregisterthevariablesstate+theresult.
        Asthedayspass,wewillbeabletodetermine,withmoreandmoreprecision,ifTDEwilleatm&m's
        foraspecificcombination:
            -didsleepverywell,alotofworkandstomachfull>Willneverhappen!
            -didn'tsleepatall,noworkatallandemptystomach>forsure!
        FollowingBayes'Theorem:theprobabilitythataneventoccurs(towin)undercertainconditionsisproportional
        totheprobabilitytowinundereachconditionseparatelyandtheprobabilitytowin.Wecomputea'Winscore'
        ->P(Won|A∩B)∝P(A∩B|Won)*P(Won)ORS(Won|A∩B)=P(A∩B|Won)*P(Won)
        Tocomputeapercentageofprobabilitytowin,wealsocomputethe'Lostscore'thatisproportionaltothe
        probabilitytoloseundereachconditionseparatelyandtheprobabilitytolose.
        ->Probability= S(Won|A∩B)/(S(Won|A∩B)+S(Lost|A∩B))
        Seehttps://www.youtube.com/watch?v=CPqOCI0ahsscanhelptogetaquickandsimpleexample.
        OneissueaboutNBCiswhenaeventoccurenceisneverobserved.
        E.g:ifwhenTDEhasanemptystomach,healwayseatm&m's,thanthe"noteatingm&m'swhenemptystomach'event
        willneverbeobserved.
        Thisiscalled'zerofrequency'andthatleadstodivision(oratleastmultiplication)byzero.
        Toavoidthis,weadd0.1ineachfrequency.Withfewdata,thecomputationisthannotreallyrealistic.
        Themorewehaverecordstoanalyse,themoretheestimationwillbeprecise.
        :return:probabilityinpercent(andintegerrounded)thattheleadwillbewonatthecurrentstage.
        """
        lead_probabilities={}
        ifnotself:
            returnlead_probabilities

        #Getallleadsvalues,nomattertheteam_id
        domain=[]
        ifbatch_mode:
            domain=[
                '&',
                    ('active','=',True),('id','in',self.ids),
                    '|',
                        ('probability','=',None),
                        '&',
                            ('probability','<',100),('probability','>',0)
            ]
        leads_values_dict=self._pls_get_lead_pls_values(domain=domain)

        ifnotleads_values_dict:
            returnlead_probabilities

        #Getuniquecouplestosearchinfrequencytableandwonleads.
        leads_fields=set() #keepuniquefields,asaleadcanhavemultipletag_ids
        won_leads=set()
        won_stage_ids=self.env['crm.stage'].search([('is_won','=',True)]).ids
        forlead_id,valuesinleads_values_dict.items():
            forfield,valueinvalues['values']:
                iffield=='stage_id'andvalueinwon_stage_ids:
                    won_leads.add(lead_id)
                leads_fields.add(field)

        #getallvariablerelatedrecordsfromfrequencytable,nomattertheteam_id
        frequencies=self.env['crm.lead.scoring.frequency'].search([('variable','in',list(leads_fields))],order="team_idasc")

        #getallteam_idsfromfrequencies
        frequency_teams=frequencies.mapped('team_id')
        frequency_team_ids=[0]+[team.idforteaminfrequency_teams]

        #1.Computeeachvariablevaluecountindividually
        #regroupeachvariabletobeabletocomputetheirownprobabilities
        #Asallthevariabledoesnotenterintoaccount(aswerejectunsetvaluesintheprocess)
        #eachvalueprobabilitymustbecomputedonlywiththeirownvariablerelatedtotalcount
        #specialcase:forleadforwhichteam_idisnotinfrequencytable,
        #weconsideralltherecords,independentlyfromteam_id(thisiswhyweaddaresult[-1])
        result=dict((team_id,dict((field,dict(won_total=0,lost_total=0))forfieldinleads_fields))forteam_idinfrequency_team_ids)
        result[-1]=dict((field,dict(won_total=0,lost_total=0))forfieldinleads_fields)
        forfrequencyinfrequencies:
            team_result=result[frequency.team_id.idiffrequency.team_idelse0]

            field=frequency['variable']
            value=frequency['value']

            #Toavoidthatatagtaketomuchimportanceifhissubsetistoosmall,
            #weignorethetagfrequenciesifwehavelessthan50wonorlostforthistag.
            iffield=='tag_id'and(frequency['won_count']+frequency['lost_count'])<50:
                continue

            team_result[field][value]={'won':frequency['won_count'],'lost':frequency['lost_count']}
            team_result[field]['won_total']+=frequency['won_count']
            team_result[field]['lost_total']+=frequency['lost_count']

            ifvaluenotinresult[-1][field]:
                result[-1][field][value]={'won':0,'lost':0}
            result[-1][field][value]['won']+=frequency['won_count']
            result[-1][field][value]['lost']+=frequency['lost_count']
            result[-1][field]['won_total']+=frequency['won_count']
            result[-1][field]['lost_total']+=frequency['lost_count']

        #Getallwon,lostandtotalcountforallrecordsinfrequenciesperteam_id
        forteam_idinresult:
            result[team_id]['team_won'],\
            result[team_id]['team_lost'],\
            result[team_id]['team_total']=self._pls_get_won_lost_total_count(result[team_id])

        save_team_id=None
        p_won,p_lost=1,1
        forlead_id,lead_valuesinleads_values_dict.items():
            #ifstage_idisnull,return0andbypasscomputation
            lead_fields=[value[0]forvalueinlead_values.get('values',[])]
            ifnot'stage_id'inlead_fields:
                lead_probabilities[lead_id]=0
                continue
            #ifleadstageiswon,return100
            eliflead_idinwon_leads:
                lead_probabilities[lead_id]=100
                continue

            lead_team_id=lead_values['team_id']iflead_values['team_id']else0 #team_id=None->Convertto0
            lead_team_id=lead_team_idiflead_team_idinresultelse-1 #team_idnotinfrequencyTable->convertto-1
            iflead_team_id!=save_team_id:
                save_team_id=lead_team_id
                team_won=result[save_team_id]['team_won']
                team_lost=result[save_team_id]['team_lost']
                team_total=result[save_team_id]['team_total']
                #ifonecount=0,wecannotcomputeleadprobability
                ifnotteam_wonornotteam_lost:
                    continue
                p_won=team_won/team_total
                p_lost=team_lost/team_total

            #2.Computewonandlostscoreusingeachvariable'sindividualprobability
            s_lead_won,s_lead_lost=p_won,p_lost
            forfield,valueinlead_values['values']:
                field_result=result.get(save_team_id,{}).get(field)
                value=value.originifhasattr(value,'origin')elsevalue
                value_result=field_result.get(str(value))iffield_resultelseFalse
                ifvalue_result:
                    total_won=team_woniffield=='stage_id'elsefield_result['won_total']
                    total_lost=team_lostiffield=='stage_id'elsefield_result['lost_total']

                    #ifonecount=0,wecannotcomputeleadprobability
                    ifnottotal_wonornottotal_lost:
                        continue
                    s_lead_won*=value_result['won']/total_won
                    s_lead_lost*=value_result['lost']/total_lost

            #3.ComputeProbabilitytowin
            probability=s_lead_won/(s_lead_won+s_lead_lost)
            lead_probabilities[lead_id]=min(max(round(100*probability,2),0.01),99.99)
        returnlead_probabilities

    #---------------------------------
    #PLS:LiveIncrement
    #---------------------------------
    def_pls_increment_frequencies(self,from_state=None,to_state=None):
        """
        Whenlosingorwinningalead,thismethodiscalledtoincrementeachPLSparameterrelatedtothelead
        inwon_count(ifwon)orinlost_count(iflost).

        Thismethodisalsousedwhenreactivatingamistakenlylostlead(usingthedecrementargument).
        Inthiscase,thelostcountshouldbede-incrementby1foreachPLSparameterlinkedotthelead.

        Liveincrementmustbedonebeforewritingthenewvaluesbecauseweneedtoknowthestatechange(fromandto).
        Thiswouldnotbeanissueforthereachwonorreachlostaswejustneedtoincrementthefrequencieswiththe
        finalstateofthelead.
        Thisissueiswhentheleadleavesaclosedstatebecauseoncethenewvalueshavebeenwriten,wedonotknow
        whatwasthepreviousstatethatweneedtodecrement.
        Thisiswhy'is_won'and'decrement'parametersareusedtodescribethefrom/tochangeofhisstate.
        """
        new_frequencies_by_team,existing_frequencies_by_team=self._pls_prepare_update_frequency_table(target_state=from_stateorto_state)

        #updatefrequencytable
        self._pls_update_frequency_table(new_frequencies_by_team,1ifto_stateelse-1,
                                         existing_frequencies_by_team=existing_frequencies_by_team)

    #---------------------------------
    #PLS:Oneshotrebuild
    #---------------------------------
    def_cron_update_automated_probabilities(self):
        """Thiscronwill:
          -rebuildtheleadscoringfrequencytable
          -recomputealltheautomated_probabilityandalignprobabilityifbothwerealigned
        """
        cron_start_date=datetime.now()
        self._rebuild_pls_frequency_table()
        self._update_automated_probabilities()
        _logger.info("PredictiveLeadScoring:Cronduration=%dseconds"%((datetime.now()-cron_start_date).total_seconds()))

    def_rebuild_pls_frequency_table(self):
        #Clearthefrequenciestable(insqltospeedupthecron)
        try:
            self.check_access_rights('unlink')
        exceptAccessError:
            raiseUserError(_("Youdon'thavetheaccessneededtorunthiscron."))
        else:
            self._cr.execute('TRUNCATETABLEcrm_lead_scoring_frequency')

        new_frequencies_by_team,unused=self._pls_prepare_update_frequency_table(rebuild=True)
        #updatefrequencytable
        self._pls_update_frequency_table(new_frequencies_by_team,1)

        _logger.info("PredictiveLeadScoring:crm.lead.scoring.frequencytablerebuilt")

    def_update_automated_probabilities(self):
        """Recomputealltheautomated_probability(andalignprobabilityifbothwerealigned)foralltheleads
        thatareactive(notwon,norlost).

        Forperformancematter,astherecanbeahugeamountofleadstorecompute,thiscronproceedbybatch.
        Eachbatchisperformedintoitsowntransaction,inordertominimisethelocktimeontheleadtable
        (andtoavoidcompletelockiftherewasonly1transactionthatwouldlastfortoolong->severalminutes).
        Ifaconcurrentupdateoccurs,itwillsimplybeputinthequeuetogetthelock.
        """
        pls_start_date=self._pls_get_safe_start_date()
        ifnotpls_start_date:
            return

        #1.Getalltheleadstorecomputecreatedafterpls_start_datethatarenorwonnorlost
        #(Won:probability=100|Lost:probability=0orinactive.Here,inactivewon'tbereturnedanyway)
        #Getalsoalltheleadwithoutprobability-->Thesearethenewleads.Activateautoprobabilityonthem.
        pending_lead_domain=[
            '&',
                '&',
                    ('stage_id','!=',False),('create_date','>=',pls_start_date),
                '|',
                    ('probability','=',False),
                    '&',
                        ('probability','<',100),('probability','>',0)
        ]
        leads_to_update=self.env['crm.lead'].search(pending_lead_domain)
        leads_to_update_count=len(leads_to_update)

        #2.Computebybatchtoavoidmemoryerror
        lead_probabilities={}
        foriinrange(0,leads_to_update_count,PLS_COMPUTE_BATCH_STEP):
            leads_to_update_part=leads_to_update[i:i+PLS_COMPUTE_BATCH_STEP]
            lead_probabilities.update(leads_to_update_part._pls_get_naive_bayes_probabilities(batch_mode=True))
        _logger.info("PredictiveLeadScoring:Newautomatedprobabilitiescomputed")

        #3.Groupbynewprobabilitytoreduceserverroundtripswhenexecutingtheupdate
        probability_leads=defaultdict(list)
        forlead_id,probabilityinsorted(lead_probabilities.items()):
            probability_leads[probability].append(lead_id)

        #4.Updateautomated_probability(+probabilityifbothwereequal)
        update_sql="""UPDATEcrm_lead
                        SETautomated_probability=%s,
                            probability=CASEWHEN(probability=automated_probabilityORprobabilityisnull)
                                               THEN(%s)
                                               ELSE(probability)
                                          END
                        WHEREidin%s"""

        #Updatebyamaximumnumberofleadsatthesametime,onebatchbytransaction:
        #-avoidmemoryerrors
        #-avoidblockingthetablefortoolongwithatoobigtransaction
        transactions_count,transactions_failed_count=0,0
        cron_update_lead_start_date=datetime.now()
        auto_commit=notgetattr(threading.currentThread(),'testing',False)
        forprobability,probability_lead_idsinprobability_leads.items():
            forlead_ids_currentintools.split_every(PLS_UPDATE_BATCH_STEP,probability_lead_ids):
                transactions_count+=1
                try:
                    self.env.cr.execute(update_sql,(probability,probability,tuple(lead_ids_current)))
                    #auto-commitexceptintestingmode
                    ifauto_commit:
                        self.env.cr.commit()
                exceptExceptionase:
                    _logger.warning("PredictiveLeadScoring:updatetransactionfailed.Error:%s"%e)
                    transactions_failed_count+=1

        _logger.info(
            "PredictiveLeadScoring:Allautomatedprobabilitiesupdated(%dleads/%dtransactions(%dfailed)/%dseconds)"%(
                leads_to_update_count,
                transactions_count,
                transactions_failed_count,
                (datetime.now()-cron_update_lead_start_date).total_seconds(),
            )
        )

    #---------------------------------
    #PLS:Commonpartsforbothmode
    #---------------------------------
    def_pls_prepare_update_frequency_table(self,rebuild=False,target_state=False):
        """
        ThismethodiscommontoLiveIncrementorFullRebuildmode,asitsharesthemainsteps.
        Thismethodwillpreparethefrequencydictneededtoupdatethefrequencytable:
            -Newfrequencies:frequenciesthatweneedtoaddinthefrequencytable.
            -Existingfrequencies:frequenciesthatarealreadyinthefrequencytable.
        Inrebuildmode,onlythenewfrequenciesareneededasexistingfrequenciesaretruncated.
        Foreachteam,eachdictcontainsthefrequencyinwonandlostforeachfield/valuecouple
        ofthetargetleads.
        Targetleadsare:
            -inLiveincrementmode:givenongoingleads(self)
            -inFullrebuildmode:alltheclosed(wonandlost)leadsintheDB.
        Duringthefrequenciesupdate,withbothnewandexistingfrequencies,wecansplitfrequenciestoupdate
        andfrequenciestoadd.Ifafield/valuecouplealreadyexistsinthefrequencytable,wejustupdateit.
        Otherwise,weneedtoinsertanewone.
        """
        #Keepeligibleleads
        pls_start_date=self._pls_get_safe_start_date()
        ifnotpls_start_date:
            return{},{}

        ifrebuild: #rebuildwilltreateveryclosedleadinDB,incrementwilltreatcurrentongoingleads
            pls_leads=self
        else:
            #OnlytreatleadscreatedafterthePLSstartDate
            pls_leads=self.filtered(
                lambdalead:fields.Date.to_date(pls_start_date)<=fields.Date.to_date(lead.create_date))
            ifnotpls_leads:
                return{},{}

        #Extracttargetleadsvalues
        ifrebuild: #rebuildisok
            domain=[
                '&',
                    ('create_date','>=',pls_start_date),
                    '|',
                        ('probability','=',100),
                        '&',
                            ('probability','=',0),('active','=',False)
              ]
            team_ids=self.env['crm.team'].with_context(active_test=False).search([]).ids+[0] #Ifteam_idisunset,consideritasteam0
        else: #increment
            domain=[('id','in',pls_leads.ids)]
            team_ids=pls_leads.mapped('team_id').ids+[0]

        leads_values_dict=pls_leads._pls_get_lead_pls_values(domain=domain)

        #splitleadsvaluesbyteam_id
        #getcurrentfrequenciesrelatedtothetargetleads
        leads_frequency_values_by_team=dict((team_id,[])forteam_idinteam_ids)
        leads_pls_fields=set() #ensuretokeepeachfieldunique(canhavemultipletag_idleads_values_dict)
        forlead_id,valuesinleads_values_dict.items():
            team_id=values.get('team_id',0) #Ifteam_idisunset,consideritasteam0
            lead_frequency_values={'count':1}
            forfield,valueinvalues['values']:
                iffield!="probability": #wasaddedtoleadvaluesinbatchmodetoknowwon/loststate,butisnotaplsfields.
                    leads_pls_fields.add(field)
                else: #extractleadprobability-neededtoincrementtag_idfrequency.(probaalwaysbeforetag_id)
                    lead_probability=value
                iffield=='tag_id': #handletag_idseparatelly(asinOneShotrebuildmode)
                    leads_frequency_values_by_team[team_id].append({field:value,'count':1,'probability':lead_probability})
                else:
                    lead_frequency_values[field]=value
            leads_frequency_values_by_team[team_id].append(lead_frequency_values)
        leads_pls_fields=list(leads_pls_fields)

        #getnewfrequencies
        new_frequencies_by_team={}
        forteam_idinteam_ids:
            #preparefieldsandtagvaluesforleadsbyteam
            new_frequencies_by_team[team_id]=self._pls_prepare_frequencies(
                leads_frequency_values_by_team[team_id],leads_pls_fields,target_state=target_state)

        #getexistingfrequencies
        existing_frequencies_by_team={}
        ifnotrebuild: #thereisnoexistingfrequencyinrebuildmodeastheywerealldeleted.
            #readallfieldstogeteverythinginmemoryinonequery(insteadofhavingquery+prefetch)
            existing_frequencies=self.env['crm.lead.scoring.frequency'].search_read(
                ['&',('variable','in',leads_pls_fields),
                      '|',('team_id','in',pls_leads.mapped('team_id').ids),('team_id','=',False)])
            forfrequencyinexisting_frequencies:
                team_id=frequency['team_id'][0]iffrequency.get('team_id')else0
                ifteam_idnotinexisting_frequencies_by_team:
                    existing_frequencies_by_team[team_id]=dict((field,{})forfieldinleads_pls_fields)

                existing_frequencies_by_team[team_id][frequency['variable']][frequency['value']]={
                    'frequency_id':frequency['id'],
                    'won':frequency['won_count'],
                    'lost':frequency['lost_count']
                }

        returnnew_frequencies_by_team,existing_frequencies_by_team

    def_pls_update_frequency_table(self,new_frequencies_by_team,step,existing_frequencies_by_team=None):
        """Create/updatethefrequencytableinacrosscompanyway,perteam_id"""
        values_to_update={}
        values_to_create=[]
        ifnotexisting_frequencies_by_team:
            existing_frequencies_by_team={}
        #buildthecreatemulti+frequenciestoupdate
        forteam_id,new_frequenciesinnew_frequencies_by_team.items():
            forfield,valueinnew_frequencies.items():
                #frequencyalreadypresent?
                current_frequencies=existing_frequencies_by_team.get(team_id,{})
                forparam,resultinvalue.items():
                    current_frequency_for_couple=current_frequencies.get(field,{}).get(param,{})
                    #Iffrequencyalreadypresent:UPDATEIT
                    ifcurrent_frequency_for_couple:
                        new_won=current_frequency_for_couple['won']+(result['won']*step)
                        new_lost=current_frequency_for_couple['lost']+(result['lost']*step)
                        #ensuretohavealwayspositivefrequencies
                        values_to_update[current_frequency_for_couple['frequency_id']]={
                            'won_count':new_wonifnew_won>0else0.1,
                            'lost_count':new_lostifnew_lost>0else0.1
                        }
                        continue

                    #Else,CREATEanewfrequencyrecord.
                    #Weadd+0.1inwonandlostcountstoavoidzerofrequencyissues
                    #shouldbe+1butitweightstoomuchonsmallrecordset.
                    values_to_create.append({
                        'variable':field,
                        'value':param,
                        'won_count':result['won']+0.1,
                        'lost_count':result['lost']+0.1,
                        'team_id':team_idifteam_idelseNone #team_id=0meansnoteam_id
                    })

        LeadScoringFrequency=self.env['crm.lead.scoring.frequency'].sudo()
        forfrequency_id,valuesinvalues_to_update.items():
            LeadScoringFrequency.browse(frequency_id).write(values)

        ifvalues_to_create:
            LeadScoringFrequency.create(values_to_create)

    #---------------------------------
    #UtilityToolsforPLS
    #---------------------------------

    #PLS: ConfigParameters
    #---------------------
    def_pls_get_safe_start_date(self):
        """Asconfig_parametersdoesnotacceptDatefield,
            wegetdirectlythedateformatedstringstoredintotheCharconfigfield,
            aswedirectlyusethisstringinthesqlqueries.
            Toavoidsqlinjectionswhenusingthisconfigparam,
            weensurethedatestringcanbeeffectivelyadate."""
        str_date=self.env['ir.config_parameter'].sudo().get_param('crm.pls_start_date')
        ifnotfields.Date.to_date(str_date):
            returnFalse
        returnstr_date

    def_pls_get_safe_fields(self):
        """Asconfig_parametersdoesnotacceptM2Mfield,
            wethefieldsfromtheformatedstringstoredintotheCharconfigfield.
            Toavoidsqlinjectionswhenusingthatlist,wereturnonlythefields
            thataredefinedonthemodel."""
        pls_fields_config=self.env['ir.config_parameter'].sudo().get_param('crm.pls_fields')
        pls_fields=pls_fields_config.split(',')ifpls_fields_configelse[]
        pls_safe_fields=[fieldforfieldinpls_fieldsiffieldinself._fields.keys()]
        returnpls_safe_fields

    #ComputeAutomatedProbabilityTools
    #-----------------------------------
    def_pls_get_won_lost_total_count(self,team_results):
        """Getallwonandalllost+total:
               firststagecanbeusedtoknowhowmanylostandwonthereis
               aswoncountareequalsforallstage
               andfirststageisalwaysincrementedinlost_count
        :paramfrequencies:lead_scoring_frequencies
        :return:woncount,lostcountandtotalcountforallrecordsinfrequencies
        """
        #TODO:checkifweneedtohandlespecificteam_idstages[forlostcount](iffirststageinsequenceisteam_specific)
        first_stage_id=self.env['crm.stage'].search([('team_id','=',False)],order='sequence',limit=1)
        ifstr(first_stage_id.id)notinteam_results.get('stage_id',[]):
            return0,0,0
        stage_result=team_results['stage_id'][str(first_stage_id.id)]
        returnstage_result['won'],stage_result['lost'],stage_result['won']+stage_result['lost']

    #PLS:RebuildFrequencyTableTools
    #----------------------------------
    def_pls_prepare_frequencies(self,lead_values,leads_pls_fields,target_state=None):
        """newstateisusedwhengettingfrequenciesforleadsthatarechangingtolostorwon.
        Staysnoneifwearecheckingfrequenciesforleadsalreadywonorlost."""
        #Frequenciesmustincludetag_id
        pls_fields=set(leads_pls_fields+['tag_id'])
        frequencies=dict((field,{})forfieldinpls_fields)

        stage_ids=self.env['crm.stage'].search_read([],['sequence','name','id'],order='sequence')
        stage_sequences={stage['id']:stage['sequence']forstageinstage_ids}

        #Incrementwon/lostfrequenciesbycriteria(field/valuecouple)
        forvaluesinlead_values:
            iftarget_state: #ignoreprobabilityvaluesiftargetstate(asprobabilityistheoldvalue)
                won_count=values['count']iftarget_state=='won'else0
                lost_count=values['count']iftarget_state=='lost'else0
            else:
                won_count=values['count']ifvalues.get('probability',0)==100else0
                lost_count=values['count']ifvalues.get('probability',1)==0 else0

            if'tag_id'invalues:
                frequencies=self._pls_increment_frequency_dict(frequencies,'tag_id',values['tag_id'],won_count,lost_count)
                continue

            #Else,treatotherfields
            if'tag_id'inpls_fields: #tag_idalreadytreatedhereabove.
                pls_fields.remove('tag_id')
            forfieldinpls_fields:
                iffieldnotinvalues:
                    continue
                value=values[field]
                ifvalueorfieldin('email_state','phone_state'):
                    iffield=='stage_id':
                        ifwon_count: #incrementallstagesifwon
                            stages_to_increment=[stage['id']forstageinstage_ids]
                        else: #incrementonlycurrent+previousstagesiflost
                            current_stage_sequence=stage_sequences[value]
                            stages_to_increment=[stage['id']forstageinstage_idsifstage['sequence']<=current_stage_sequence]
                        forstage_idinstages_to_increment:
                            frequencies=self._pls_increment_frequency_dict(frequencies,field,stage_id,won_count,lost_count)
                    else:
                        frequencies=self._pls_increment_frequency_dict(frequencies,field,value,won_count,lost_count)

        returnfrequencies

    def_pls_increment_frequency_dict(self,frequencies,field,value,won,lost):
        value=str(value) #Ensurewewillalwayscomparestrings.
        ifvaluenotinfrequencies[field]:
            frequencies[field][value]={'won':won,'lost':lost}
        else:
            frequencies[field][value]['won']+=won
            frequencies[field][value]['lost']+=lost
        returnfrequencies

    #CommonPLSTools
    #----------------
    def_pls_get_lead_pls_values(self,domain=[]):
        """
        Thismethodsbuildsadictwhere,foreachleadinselformatchingthegivendomain,
        wewillgetalistoffield/valuecouple.
        Duetoonchangeandcreate,wedon'talwayshavetheidoftheleadtorecompute.
        Whenweupdatefewrecords(one,typically)withonchanges,webuildthelead_values(=couplefield/value)
        usingtheORM.
        TospeedupthecomputationandavoidmakingtoomuchDBreadinsideloops,
        wecangiveadomaintomakesqlqueriestobypasstheORM.
        Thisdomainwillbeusedinsqlqueriestogetthevaluesforeveryleadmatchingthedomain.
        :paramdomain:Ifset,wegetalltheleadsvaluesviauniquesqlqueries(onefortags,oneforotherfields),
                            usingthegivendomainonleads.
                       Ifnotset,getleadvaluesleadbyleadusingtheORM.
        :return:{lead_id:[(field1:value1),(field2:value2),...],...}
        """
        leads_values_dict=OrderedDict()
        pls_fields=["stage_id","team_id"]+self._pls_get_safe_fields()

        ifdomain:
            #active_test=Falseasdomainshouldtakeactiveinto'active'fielditself
            from_clause,where_clause,where_params=self.env['crm.lead'].with_context(active_test=False)._where_calc(domain).get_sql()
            str_fields=",".join(["{}"]*len(pls_fields))
            args=[sql.Identifier(field)forfieldinpls_fields]

            #Getleadsvalues
            self.flush(['probability'])
            query="""SELECTid,probability,%s
                        FROM%s
                        WHERE%sorderbyteam_idasc"""
            query=sql.SQL(query%(str_fields,from_clause,where_clause)).format(*args)
            self._cr.execute(query,where_params)
            lead_results=self._cr.dictfetchall()

            #Gettagsvalues
            query="""SELECTcrm_lead.idaslead_id,t.idastag_id
                            FROM%s
                            LEFTJOINcrm_tag_relrelONcrm_lead.id=rel.lead_id
                            LEFTJOINcrm_tagtONrel.tag_id=t.id
                            WHERE%sorderbycrm_lead.team_idasc"""
            query=sql.SQL(query%(from_clause,where_clause)).format(*args)
            self._cr.execute(query,where_params)
            tag_results=self._cr.dictfetchall()

            #getall(variable,value)coupleforallinself
            forleadinlead_results:
                lead_values=[]
                forfieldinpls_fields+['probability']: #addprobabilityasusedin_pls_prepare_frequencies(neededinrebuildmode)
                    value=lead[field]
                    iffield=='team_id': #ignoreteam_idasstoredseparatelyinleads_values_dict[lead_id][team_id]
                        continue
                    ifvalueorfield=='probability': #0isacorrectvalueforprobability
                        lead_values.append((field,value))
                    eliffieldin('email_state','phone_state'): #AsORMreads'None'as'False',dothesamehere
                        lead_values.append((field,False))
                    leads_values_dict[lead['id']]={'values':lead_values,'team_id':lead['team_id']or0}

            fortagintag_results:
                iftag['tag_id']:
                    leads_values_dict[tag['lead_id']]['values'].append(('tag_id',tag['tag_id']))
            returnleads_values_dict
        else:
            forleadinself:
                lead_values=[]
                forfieldinpls_fields:
                    iffield=='team_id': #ignoreteam_idasstoredseparatelyinleads_values_dict[lead_id][team_id]
                        continue
                    value=lead[field].idifisinstance(lead[field],models.BaseModel)elselead[field]
                    ifvalueorfieldin('email_state','phone_state'):
                        lead_values.append((field,value))
                fortaginlead.tag_ids:
                    lead_values.append(('tag_id',tag.id))
                leads_values_dict[lead.id]={'values':lead_values,'team_id':lead['team_id'].id}
            returnleads_values_dict
