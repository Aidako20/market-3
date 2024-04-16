#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson

frombabel.datesimportformat_date
fromdatetimeimportdate
fromdateutil.relativedeltaimportrelativedelta

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError
fromflectra.releaseimportversion


classCrmTeam(models.Model):
    _name="crm.team"
    _inherit=['mail.thread']
    _description="SalesTeam"
    _order="sequence"
    _check_company_auto=True

    def_get_default_team_id(self,user_id=None,domain=None):
        user_id=user_idorself.env.uid
        user_salesteam_id=self.env['res.users'].browse(user_id).sale_team_id.id
        #Avoidsearchingonmember_ids(+1query)whenwemayhavetheusersalesteamalreadyincache.
        team=self.env['crm.team'].search([
            ('company_id','in',[False,self.env.company.id]),
            '|',('user_id','=',user_id),('id','=',user_salesteam_id),
        ],limit=1)
        ifnotteamand'default_team_id'inself.env.context:
            team=self.env['crm.team'].browse(self.env.context.get('default_team_id'))
        returnteamorself.env['crm.team'].search(domainor[],limit=1)

    def_get_default_favorite_user_ids(self):
        return[(6,0,[self.env.uid])]

    name=fields.Char('SalesTeam',required=True,translate=True)
    sequence=fields.Integer('Sequence',default=10)
    active=fields.Boolean(default=True,help="Iftheactivefieldissettofalse,itwillallowyoutohidetheSalesTeamwithoutremovingit.")
    company_id=fields.Many2one(
        'res.company',string='Company',index=True,
        default=lambdaself:self.env.company)
    currency_id=fields.Many2one(
        "res.currency",string="Currency",
        related='company_id.currency_id',readonly=True)
    user_id=fields.Many2one('res.users',string='TeamLeader',check_company=True)
    #memberships
    member_ids=fields.One2many(
        'res.users','sale_team_id',string='ChannelMembers',
        check_company=True,domain=[('share','=',False)],
        help="Addmemberstoautomaticallyassigntheirdocumentstothissalesteam.Youcanonlybememberofoneteam.")
    #UXoptions
    color=fields.Integer(string='ColorIndex',help="Thecolorofthechannel")
    favorite_user_ids=fields.Many2many(
        'res.users','team_favorite_user_rel','team_id','user_id',
        string='FavoriteMembers',default=_get_default_favorite_user_ids)
    is_favorite=fields.Boolean(
        string='Showondashboard',compute='_compute_is_favorite',inverse='_inverse_is_favorite',
        help="Favoriteteamstodisplaytheminthedashboardandaccessthemeasily.")
    dashboard_button_name=fields.Char(string="DashboardButton",compute='_compute_dashboard_button_name')
    dashboard_graph_data=fields.Text(compute='_compute_dashboard_graph')

    def_compute_is_favorite(self):
        forteaminself:
            team.is_favorite=self.env.userinteam.favorite_user_ids

    def_inverse_is_favorite(self):
        sudoed_self=self.sudo()
        to_fav=sudoed_self.filtered(lambdateam:self.env.usernotinteam.favorite_user_ids)
        to_fav.write({'favorite_user_ids':[(4,self.env.uid)]})
        (sudoed_self-to_fav).write({'favorite_user_ids':[(3,self.env.uid)]})
        returnTrue

    def_compute_dashboard_button_name(self):
        """SetstheadequatedashboardbuttonnamedependingontheSalesTeam'soptions
        """
        forteaminself:
            team.dashboard_button_name=_("BigPrettyButton:)")#placeholder

    def_compute_dashboard_graph(self):
        forteaminself:
            team.dashboard_graph_data=json.dumps(team._get_dashboard_graph_data())

    #------------------------------------------------------------
    #CRUD
    #------------------------------------------------------------

    @api.model
    defcreate(self,values):
        team=super(CrmTeam,self.with_context(mail_create_nosubscribe=True)).create(values)
        ifvalues.get('member_ids'):
            team._add_members_to_favorites()
        returnteam

    defwrite(self,values):
        res=super(CrmTeam,self).write(values)
        ifvalues.get('member_ids'):
            self._add_members_to_favorites()
        returnres

    defunlink(self):
        default_teams=[
            self.env.ref('sales_team.salesteam_website_sales'),
            self.env.ref('sales_team.pos_sales_team'),
            self.env.ref('sales_team.ebay_sales_team')
        ]
        forteaminself:
            ifteamindefault_teams:
                raiseUserError(_('Cannotdeletedefaultteam"%s"',team.name))
        returnsuper(CrmTeam,self).unlink()

    #------------------------------------------------------------
    #ACTIONS
    #------------------------------------------------------------

    defaction_primary_channel_button(self):
        """SkeletonfunctiontobeoverloadedItwillreturntheadequateaction
        dependingontheSalesTeam'soptions."""
        returnFalse

    #------------------------------------------------------------
    #TOOLS
    #------------------------------------------------------------

    def_add_members_to_favorites(self):
        forteaminself:
            team.favorite_user_ids=[(4,member.id)formemberinteam.member_ids]

    #------------------------------------------------------------
    #GRAPH
    #------------------------------------------------------------

    def_graph_get_model(self):
        """skeletonfunctiondefinedherebecauseit'llbecalledbycrmand/orsale
        """
        raiseUserError(_('UndefinedgraphmodelforSalesTeam:%s',self.name))

    def_graph_get_dates(self,today):
        """returnacoherentstartandenddateforthedashboardgraphcoveringamonthperiodgroupedbyweek.
        """
        start_date=today-relativedelta(months=1)
        #wetakethestartofthefollowingweekifwegroupbyweek
        #(toavoidhavingtwicethesameweekfromdifferentmonth)
        start_date+=relativedelta(days=8-start_date.isocalendar()[2])
        return[start_date,today]

    def_graph_date_column(self):
        return'create_date'

    def_graph_x_query(self):
        return'EXTRACT(WEEKFROM%s)'%self._graph_date_column()

    def_graph_y_query(self):
        raiseUserError(_('UndefinedgraphmodelforSalesTeam:%s',self.name))

    def_extra_sql_conditions(self):
        return''

    def_graph_title_and_key(self):
        """Returnsanarraycontainingtheappropriategraphtitleandkeyrespectively.

            ThekeyisforlineCharts,tohavetheon-hoverlabel.
        """
        return['','']

    def_graph_data(self,start_date,end_date):
        """returnformatshouldbeaniterableofdictsthatcontain{'x_value':...,'y_value':...}
            x_valuesshouldbeweeks.
            y_valuesarefloats.
        """
        query="""SELECT%(x_query)sasx_value,%(y_query)sasy_value
                     FROM%(table)s
                    WHEREteam_id=%(team_id)s
                      ANDDATE(%(date_column)s)>=%(start_date)s
                      ANDDATE(%(date_column)s)<=%(end_date)s
                      %(extra_conditions)s
                    GROUPBYx_value;"""

        #applyrules
        dashboard_graph_model=self._graph_get_model()
        GraphModel=self.env[dashboard_graph_model]
        graph_table=GraphModel._table
        extra_conditions=self._extra_sql_conditions()
        where_query=GraphModel._where_calc([])
        GraphModel._apply_ir_rules(where_query,'read')
        from_clause,where_clause,where_clause_params=where_query.get_sql()
        ifwhere_clause:
            extra_conditions+="AND"+where_clause

        query=query%{
            'x_query':self._graph_x_query(),
            'y_query':self._graph_y_query(),
            'table':graph_table,
            'team_id':"%s",
            'date_column':self._graph_date_column(),
            'start_date':"%s",
            'end_date':"%s",
            'extra_conditions':extra_conditions
        }

        self._cr.execute(query,[self.id,start_date,end_date]+where_clause_params)
        returnself.env.cr.dictfetchall()

    def_get_dashboard_graph_data(self):
        defget_week_name(start_date,locale):
            """Generatesaweekname(string)fromadatetimeaccordingtothelocale:
                E.g.:locale   start_date(datetime)     returnstring
                      "en_US"     November16th          "16-22Nov"
                      "en_US"     December28th          "28Dec-3Jan"
            """
            if(start_date+relativedelta(days=6)).month==start_date.month:
                short_name_from=format_date(start_date,'d',locale=locale)
            else:
                short_name_from=format_date(start_date,'dMMM',locale=locale)
            short_name_to=format_date(start_date+relativedelta(days=6),'dMMM',locale=locale)
            returnshort_name_from+'-'+short_name_to

        self.ensure_one()
        values=[]
        today=fields.Date.from_string(fields.Date.context_today(self))
        start_date,end_date=self._graph_get_dates(today)
        graph_data=self._graph_data(start_date,end_date)
        x_field='label'
        y_field='value'

        #generateallrequiredx_fieldsandupdatethey_valueswherewehavedataforthem
        locale=self._context.get('lang')or'en_US'

        weeks_in_start_year=int(date(start_date.year,12,28).isocalendar()[1])#ThisdateisalwaysinthelastweekofISOyears
        forweekinrange(0,(end_date.isocalendar()[1]-start_date.isocalendar()[1])%weeks_in_start_year+1):
            short_name=get_week_name(start_date+relativedelta(days=7*week),locale)
            values.append({x_field:short_name,y_field:0})

        fordata_itemingraph_data:
            index=int((data_item.get('x_value')-start_date.isocalendar()[1])%weeks_in_start_year)
            values[index][y_field]=data_item.get('y_value')

        [graph_title,graph_key]=self._graph_title_and_key()
        color='#009EFB'if'+e'inversionelse'#7c7bad'
        return[{'values':values,'area':True,'title':graph_title,'key':graph_key,'color':color}]
