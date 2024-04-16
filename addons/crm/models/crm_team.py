#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importast
importdatetime

fromflectraimportapi,fields,models,_
fromflectra.tools.safe_evalimportsafe_eval


classTeam(models.Model):
    _name='crm.team'
    _inherit=['mail.alias.mixin','crm.team']
    _description='SalesTeam'

    use_leads=fields.Boolean('Leads',help="Checkthisboxtofilterandqualifyincomingrequestsasleadsbeforeconvertingthemintoopportunitiesandassigningthemtoasalesperson.")
    use_opportunities=fields.Boolean('Pipeline',default=True,help="Checkthisboxtomanageapresalesprocesswithopportunities.")
    alias_id=fields.Many2one(
        'mail.alias',string='Alias',ondelete="restrict",required=True,
        help="Theemailaddressassociatedwiththischannel.Newemailsreceivedwillautomaticallycreatenewleadsassignedtothechannel.")
    #statisticsaboutleads/opportunities/both
    lead_unassigned_count=fields.Integer(
        string='#UnassignedLeads',compute='_compute_lead_unassigned_count')
    lead_all_assigned_month_count=fields.Integer(
        string='#Leads/Oppsassignedthismonth',compute='_compute_lead_all_assigned_month_count',
        help="Numberofleadsandopportunitiesassignedthislastmonth.")
    opportunities_count=fields.Integer(
        string='#Opportunities',compute='_compute_opportunities_data')
    opportunities_amount=fields.Monetary(
        string='OpportunitiesRevenues',compute='_compute_opportunities_data')
    opportunities_overdue_count=fields.Integer(
        string='#OverdueOpportunities',compute='_compute_opportunities_overdue_data')
    opportunities_overdue_amount=fields.Monetary(
        string='OverdueOpportunitiesRevenues',compute='_compute_opportunities_overdue_data',)
    #alias:improvefieldscomingfrom_inherits,useinheritedtoavoidreplacingthem
    alias_user_id=fields.Many2one(
        'res.users',related='alias_id.alias_user_id',inherited=True,
        domain=lambdaself:[('groups_id','in',self.env.ref('sales_team.group_sale_salesman_all_leads').id)])

    def_compute_lead_unassigned_count(self):
        leads_data=self.env['crm.lead'].read_group([
            ('team_id','in',self.ids),
            ('type','=','lead'),
            ('user_id','=',False),
        ],['team_id'],['team_id'])
        counts={datum['team_id'][0]:datum['team_id_count']fordatuminleads_data}
        forteaminself:
            team.lead_unassigned_count=counts.get(team.id,0)

    def_compute_lead_all_assigned_month_count(self):
        limit_date=datetime.datetime.now()-datetime.timedelta(days=30)
        leads_data=self.env['crm.lead'].read_group([
            ('team_id','in',self.ids),
            ('date_open','>=',fields.Datetime.to_string(limit_date)),
            ('user_id','!=',False),
        ],['team_id'],['team_id'])
        counts={datum['team_id'][0]:datum['team_id_count']fordatuminleads_data}
        forteaminself:
            team.lead_all_assigned_month_count=counts.get(team.id,0)

    def_compute_opportunities_data(self):
        opportunity_data=self.env['crm.lead'].read_group([
            ('team_id','in',self.ids),
            ('probability','<',100),
            ('type','=','opportunity'),
        ],['expected_revenue:sum','team_id'],['team_id'])
        counts={datum['team_id'][0]:datum['team_id_count']fordatuminopportunity_data}
        amounts={datum['team_id'][0]:datum['expected_revenue']fordatuminopportunity_data}
        forteaminself:
            team.opportunities_count=counts.get(team.id,0)
            team.opportunities_amount=amounts.get(team.id,0)

    def_compute_opportunities_overdue_data(self):
        opportunity_data=self.env['crm.lead'].read_group([
            ('team_id','in',self.ids),
            ('probability','<',100),
            ('type','=','opportunity'),
            ('date_deadline','<',fields.Date.to_string(fields.Datetime.now()))
        ],['expected_revenue','team_id'],['team_id'])
        counts={datum['team_id'][0]:datum['team_id_count']fordatuminopportunity_data}
        amounts={datum['team_id'][0]:(datum['expected_revenue'])fordatuminopportunity_data}
        forteaminself:
            team.opportunities_overdue_count=counts.get(team.id,0)
            team.opportunities_overdue_amount=amounts.get(team.id,0)

    @api.onchange('use_leads','use_opportunities')
    def_onchange_use_leads_opportunities(self):
        ifnotself.use_leadsandnotself.use_opportunities:
            self.alias_name=False

    #------------------------------------------------------------
    #ORM
    #------------------------------------------------------------

    defwrite(self,vals):
        result=super(Team,self).write(vals)
        if'use_leads'invalsor'use_opportunities'invals:
            forteaminself:
                alias_vals=team._alias_get_creation_values()
                team.write({
                    'alias_name':alias_vals.get('alias_name',team.alias_name),
                    'alias_defaults':alias_vals.get('alias_defaults'),
                })
        returnresult

    #------------------------------------------------------------
    #MESSAGING
    #------------------------------------------------------------

    def_alias_get_creation_values(self):
        values=super(Team,self)._alias_get_creation_values()
        values['alias_model_id']=self.env['ir.model']._get('crm.lead').id
        ifself.id:
            ifnotself.use_leadsandnotself.use_opportunities:
                values['alias_name']=False
            values['alias_defaults']=defaults=ast.literal_eval(self.alias_defaultsor"{}")
            has_group_use_lead=self.env.user.has_group('crm.group_use_lead')
            defaults['type']='lead'ifhas_group_use_leadandself.use_leadselse'opportunity'
            defaults['team_id']=self.id
        returnvalues

    #------------------------------------------------------------
    #ACTIONS
    #------------------------------------------------------------

    #TODOJEM:refactorthisstuffwithxmlaction,propercustomization,
    @api.model
    defaction_your_pipeline(self):
        action=self.env["ir.actions.actions"]._for_xml_id("crm.crm_lead_action_pipeline")
        user_team_id=self.env.user.sale_team_id.id
        ifuser_team_id:
            #Toensurethattheteamisreadableinmulticompany
            user_team_id=self.search([('id','=',user_team_id)],limit=1).id
        else:
            user_team_id=self.search([],limit=1).id
            action['help']=_("""<pclass='o_view_nocontent_smiling_face'>Addnewopportunities</p><p>
    LookslikeyouarenotamemberofaSalesTeam.Youshouldaddyourself
    asamemberofoneoftheSalesTeam.
</p>""")
            ifuser_team_id:
                action['help']+=_("<p>Asyoudon'tbelongtoanySalesTeam,Flectraopensthefirstonebydefault.</p>")

        action_context=safe_eval(action['context'],{'uid':self.env.uid})
        ifuser_team_id:
            action_context['default_team_id']=user_team_id

        action['context']=action_context
        returnaction

    def_compute_dashboard_button_name(self):
        super(Team,self)._compute_dashboard_button_name()
        team_with_pipelines=self.filtered(lambdael:el.use_opportunities)
        team_with_pipelines.update({'dashboard_button_name':_("Pipeline")})

    defaction_primary_channel_button(self):
        ifself.use_opportunities:
            returnself.env["ir.actions.actions"]._for_xml_id("crm.crm_case_form_view_salesteams_opportunity")
        returnsuper(Team,self).action_primary_channel_button()

    def_graph_get_model(self):
        ifself.use_opportunities:
            return'crm.lead'
        returnsuper(Team,self)._graph_get_model()

    def_graph_date_column(self):
        ifself.use_opportunities:
            return'create_date'
        returnsuper(Team,self)._graph_date_column()

    def_graph_y_query(self):
        ifself.use_opportunities:
            return'count(*)'
        returnsuper(Team,self)._graph_y_query()

    def_extra_sql_conditions(self):
        ifself.use_opportunities:
            return"ANDtypeLIKE'opportunity'"
        returnsuper(Team,self)._extra_sql_conditions()

    def_graph_title_and_key(self):
        ifself.use_opportunities:
            return['',_('NewOpportunities')]#nomoretitle
        returnsuper(Team,self)._graph_title_and_key()
