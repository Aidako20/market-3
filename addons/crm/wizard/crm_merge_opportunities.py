#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classMergeOpportunity(models.TransientModel):
    """
        Mergeopportunitiestogether.
        Ifwe'retalkingaboutopportunities,it'sjustbecauseitmakesmoresense
        tomergeoppsthanleads,becausetheleadsaremoreephemeralobjects.
        Butsinceopportunitiesareleads,it'salsopossibletomergeleads
        together(resultinginanewlead),orleadsandoppstogether(resulting
        inanewopp).
    """

    _name='crm.merge.opportunity'
    _description='MergeOpportunities'

    @api.model
    defdefault_get(self,fields):
        """Useactive_idsfromthecontexttofetchtheleads/oppstomerge.
            Inordertogetmerged,theseleads/oppscan'tbein'Dead'or'Closed'
        """
        record_ids=self._context.get('active_ids')
        result=super(MergeOpportunity,self).default_get(fields)

        ifrecord_ids:
            if'opportunity_ids'infields:
                opp_ids=self.env['crm.lead'].browse(record_ids).filtered(lambdaopp:opp.probability<100).ids
                result['opportunity_ids']=[(6,0,opp_ids)]

        returnresult

    opportunity_ids=fields.Many2many('crm.lead','merge_opportunity_rel','merge_id','opportunity_id',string='Leads/Opportunities')
    user_id=fields.Many2one('res.users','Salesperson',index=True)
    team_id=fields.Many2one(
        'crm.team','SalesTeam',index=True,
        compute='_compute_team_id',readonly=False,store=True)

    defaction_merge(self):
        self.ensure_one()
        merge_opportunity=self.opportunity_ids.merge_opportunity(self.user_id.id,self.team_id.id)
        returnmerge_opportunity.redirect_lead_opportunity_view()

    @api.depends('user_id')
    def_compute_team_id(self):
        """Whenchangingtheuser,alsosetateam_idorrestrictteamid
            totheonesuser_idismemberof."""
        forwizardinself:
            ifwizard.user_id:
                user_in_team=False
                ifwizard.team_id:
                    user_in_team=wizard.env['crm.team'].search_count([('id','=',wizard.team_id.id),'|',('user_id','=',wizard.user_id.id),('member_ids','=',wizard.user_id.id)])
                ifnotuser_in_team:
                    wizard.team_id=wizard.env['crm.team'].search(['|',('user_id','=',wizard.user_id.id),('member_ids','=',wizard.user_id.id)],limit=1)                   
