#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classLead2OpportunityMassConvert(models.TransientModel):
    _name='crm.lead2opportunity.partner.mass'
    _description='ConvertLeadtoOpportunity(inmass)'
    _inherit='crm.lead2opportunity.partner'

    lead_id=fields.Many2one(required=False)
    lead_tomerge_ids=fields.Many2many(
        'crm.lead','crm_convert_lead_mass_lead_rel',
        string='ActiveLeads',context={'active_test':False},
        default=lambdaself:self.env.context.get('active_ids',[]),
    )
    user_ids=fields.Many2many('res.users',string='Salespersons')
    deduplicate=fields.Boolean('Applydeduplication',default=True,help='Mergewithexistingleads/opportunitiesofeachpartner')
    action=fields.Selection(selection_add=[
        ('each_exist_or_create','Useexistingpartnerorcreate'),
    ],string='RelatedCustomer',ondelete={
        'each_exist_or_create':lambdarecs:recs.write({'action':'exist'}),
    })
    force_assignment=fields.Boolean(default=False)

    @api.depends('duplicated_lead_ids')
    def_compute_name(self):
        forconvertinself:
            convert.name='convert'

    @api.depends('lead_tomerge_ids')
    def_compute_action(self):
        forconvertinself:
            convert.action='each_exist_or_create'

    @api.depends('lead_tomerge_ids')
    def_compute_partner_id(self):
        forconvertinself:
            convert.partner_id=False

    @api.depends('user_ids')
    def_compute_team_id(self):
        """Whenchangingtheuser,alsosetateam_idorrestrictteamid
        totheonesuser_idismemberof."""
        forconvertinself:
            #settinguserasvoidshouldnottriggeranewteamcomputation
            ifnotconvert.user_idandnotconvert.user_idsandconvert.team_id:
                continue
            user=convert.user_idorconvert.user_idsandconvert.user_ids[0]orself.env.user
            ifconvert.team_idanduserinconvert.team_id.member_ids|convert.team_id.user_id:
                continue
            team_domain=[]
            team=self.env['crm.team']._get_default_team_id(user_id=user.id,domain=team_domain)
            convert.team_id=team.id

    @api.depends('lead_tomerge_ids')
    def_compute_duplicated_lead_ids(self):
        forconvertinself:
            duplicated=self.env['crm.lead']
            forleadinconvert.lead_tomerge_ids:
                duplicated_leads=self.env['crm.lead']._get_lead_duplicates(
                    partner=lead.partner_id,
                    email=lead.partner_idandlead.partner_id.emailorlead.email_from,
                    include_lost=False)
                iflen(duplicated_leads)>1:
                    duplicated+=lead
            convert.duplicated_lead_ids=duplicated.ids

    def_convert_and_allocate(self,leads,user_ids,team_id=False):
        """When"massively"(morethanoneatatime)convertingleadsto
        opportunities,checkthesalesteam_idandsalesmen_idsandupdate
        thevaluesbeforecallingsuper.
        """
        self.ensure_one()
        salesmen_ids=[]
        ifself.user_ids:
            salesmen_ids=self.user_ids.ids
        returnsuper(Lead2OpportunityMassConvert,self)._convert_and_allocate(leads,salesmen_ids,team_id=team_id)

    defaction_mass_convert(self):
        self.ensure_one()
        ifself.name=='convert'andself.deduplicate:
            #TDECLEANME:stillusingactive_idsfromcontext
            active_ids=self._context.get('active_ids',[])
            merged_lead_ids=set()
            remaining_lead_ids=set()
            forleadinself.lead_tomerge_ids:
                ifleadnotinmerged_lead_ids:
                    duplicated_leads=self.env['crm.lead']._get_lead_duplicates(
                        partner=lead.partner_id,
                        email=lead.partner_id.emailorlead.email_from,
                        include_lost=False
                    )
                    iflen(duplicated_leads)>1:
                        lead=duplicated_leads.merge_opportunity()
                        merged_lead_ids.update(duplicated_leads.ids)
                        remaining_lead_ids.add(lead.id)
            #rebuildlistofleadIDStoconvert,followinggivenorder
            final_ids=[lead_idforlead_idinactive_idsiflead_idnotinmerged_lead_ids]
            final_ids+=[lead_idforlead_idinremaining_lead_idsiflead_idnotinfinal_ids]

            self=self.with_context(active_ids=final_ids) #onlyupdateactive_idswhenthereareset
        returnself.action_apply()

    def_convert_handle_partner(self,lead,action,partner_id):
        ifself.action=='each_exist_or_create':
            partner_id=lead._find_matching_partner(email_only=True).id
            action='create'
        returnsuper(Lead2OpportunityMassConvert,self)._convert_handle_partner(lead,action,partner_id)
