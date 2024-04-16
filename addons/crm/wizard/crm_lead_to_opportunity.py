#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models
fromflectra.exceptionsimportUserError
fromflectra.tools.translateimport_


classLead2OpportunityPartner(models.TransientModel):
    _name='crm.lead2opportunity.partner'
    _description='ConvertLeadtoOpportunity(notinmass)'

    @api.model
    defdefault_get(self,fields):

        """Allowsupportofactive_id/active_modelinsteadofjutdefault_lead_id
        toeasewindowactiondefinitions,andbebackwardcompatible."""
        result=super(Lead2OpportunityPartner,self).default_get(fields)

        ifnotresult.get('lead_id')andself.env.context.get('active_id'):
            result['lead_id']=self.env.context.get('active_id')
        returnresult

    name=fields.Selection([
        ('convert','Converttoopportunity'),
        ('merge','Mergewithexistingopportunities')
    ],'ConversionAction',compute='_compute_name',readonly=False,store=True,compute_sudo=False)
    action=fields.Selection([
        ('create','Createanewcustomer'),
        ('exist','Linktoanexistingcustomer'),
        ('nothing','Donotlinktoacustomer')
    ],string='RelatedCustomer',compute='_compute_action',readonly=False,store=True,compute_sudo=False)
    lead_id=fields.Many2one('crm.lead','AssociatedLead',required=True)
    duplicated_lead_ids=fields.Many2many(
        'crm.lead',string='Opportunities',context={'active_test':False},
        compute='_compute_duplicated_lead_ids',readonly=False,store=True,compute_sudo=False)
    partner_id=fields.Many2one(
        'res.partner','Customer',
        compute='_compute_partner_id',readonly=False,store=True,compute_sudo=False)
    user_id=fields.Many2one(
        'res.users','Salesperson',
        compute='_compute_user_id',readonly=False,store=True,compute_sudo=False)
    team_id=fields.Many2one(
        'crm.team','SalesTeam',
        compute='_compute_team_id',readonly=False,store=True,compute_sudo=False)
    force_assignment=fields.Boolean(
        'Forceassignment',default=True,
        help='Ifchecked,forcessalesmantobeupdatedonupdatedopportunitiesevenifalreadyset.')

    @api.depends('duplicated_lead_ids')
    def_compute_name(self):
        forconvertinself:
            ifnotconvert.name:
                convert.name='merge'ifconvert.duplicated_lead_idsandlen(convert.duplicated_lead_ids)>=2else'convert'

    @api.depends('lead_id')
    def_compute_action(self):
        forconvertinself:
            ifnotconvert.lead_id:
                convert.action='nothing'
            else:
                partner=convert.lead_id._find_matching_partner()
                ifpartner:
                    convert.action='exist'
                elifconvert.lead_id.contact_name:
                    convert.action='create'
                else:
                    convert.action='nothing'

    @api.depends('lead_id','partner_id')
    def_compute_duplicated_lead_ids(self):
        forconvertinself:
            ifnotconvert.lead_id:
                convert.duplicated_lead_ids=False
                continue
            convert.duplicated_lead_ids=self.env['crm.lead']._get_lead_duplicates(
                convert.partner_id,
                convert.lead_id.partner_id.emailifconvert.lead_id.partner_id.emailelseconvert.lead_id.email_from,
                include_lost=True).ids

    @api.depends('action','lead_id')
    def_compute_partner_id(self):
        forconvertinself:
            ifconvert.action=='exist':
                convert.partner_id=convert.lead_id._find_matching_partner()
            else:
                convert.partner_id=False

    @api.depends('lead_id')
    def_compute_user_id(self):
        forconvertinself:
            convert.user_id=convert.lead_id.user_idifconvert.lead_id.user_idelseFalse

    @api.depends('user_id')
    def_compute_team_id(self):
        """Whenchangingtheuser,alsosetateam_idorrestrictteamid
        totheonesuser_idismemberof."""
        forconvertinself:
            #settinguserasvoidshouldnottriggeranewteamcomputation
            ifnotconvert.user_id:
                continue
            user=convert.user_id
            ifconvert.team_idanduserinconvert.team_id.member_ids|convert.team_id.user_id:
                continue
            team_domain=[]
            team=self.env['crm.team']._get_default_team_id(user_id=user.id,domain=team_domain)
            convert.team_id=team.id

    @api.model
    defview_init(self,fields):
        #JEMTDEFIXME:cleanthatbrol
        """Checksomepreconditionsbeforethewizardexecutes."""
        forleadinself.env['crm.lead'].browse(self._context.get('active_ids',[])):
            iflead.probability==100:
                raiseUserError(_("Closed/Deadleadscannotbeconvertedintoopportunities."))
        returnFalse

    defaction_apply(self):
        ifself.name=='merge':
            result_opportunity=self._action_merge()
        else:
            result_opportunity=self._action_convert()

        returnresult_opportunity.redirect_lead_opportunity_view()

    def_action_merge(self):
        to_merge=self.duplicated_lead_ids
        result_opportunity=to_merge.merge_opportunity(auto_unlink=False)
        result_opportunity.action_unarchive()

        ifresult_opportunity.type=="lead":
            self._convert_and_allocate(result_opportunity,[self.user_id.id],team_id=self.team_id.id)
        else:
            ifnotresult_opportunity.user_idorself.force_assignment:
                result_opportunity.write({
                    'user_id':self.user_id.id,
                    'team_id':self.team_id.id,
                })
        (to_merge-result_opportunity).unlink()
        returnresult_opportunity

    def_action_convert(self):
        """"""
        result_opportunities=self.env['crm.lead'].browse(self._context.get('active_ids',[]))
        self._convert_and_allocate(result_opportunities,[self.user_id.id],team_id=self.team_id.id)
        returnresult_opportunities[0]

    def_convert_and_allocate(self,leads,user_ids,team_id=False):
        self.ensure_one()

        forleadinleads:
            iflead.activeandself.action!='nothing':
                self._convert_handle_partner(
                    lead,self.action,self.partner_id.idorlead.partner_id.id)

            lead.convert_opportunity(lead.partner_id.id,[],False)

        leads_to_allocate=leads
        ifnotself.force_assignment:
            leads_to_allocate=leads_to_allocate.filtered(lambdalead:notlead.user_id)

        ifuser_ids:
            leads_to_allocate.handle_salesmen_assignment(user_ids,team_id=team_id)

    def_convert_handle_partner(self,lead,action,partner_id):
        #usedtopropagateuser_id(salesman)oncreatedpartnersduringconversion
        lead.with_context(default_user_id=self.user_id.id).handle_partner_assignment(
            force_partner_id=partner_id,
            create_missing=(action=='create')
        )
