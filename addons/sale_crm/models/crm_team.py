#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api,_


classCrmTeam(models.Model):
    _inherit='crm.team'

    def_compute_dashboard_button_name(self):
        super(CrmTeam,self)._compute_dashboard_button_name()
        teams_with_opp=self.filtered(lambdateam:team.use_opportunities)
        ifself._context.get('in_sales_app'):
            teams_with_opp.update({'dashboard_button_name':_("SalesAnalysis")})

    defaction_primary_channel_button(self):
        ifself._context.get('in_sales_app')andself.use_opportunities:
            returnself.env["ir.actions.actions"]._for_xml_id("sale.action_order_report_so_salesteam")
        returnsuper(CrmTeam,self).action_primary_channel_button()
    
    def_graph_get_model(self):
        ifself.use_opportunitiesandself._context.get('in_sales_app'):
            return'sale.report'
        returnsuper(CrmTeam,self)._graph_get_model()

    def_graph_date_column(self):
        ifself.use_opportunitiesandself._context.get('in_sales_app'):
            return'date'
        returnsuper(CrmTeam,self)._graph_date_column()

    def_graph_y_query(self):
        ifself.use_opportunitiesandself._context.get('in_sales_app'):
            return'SUM(price_subtotal)'
        returnsuper(CrmTeam,self)._graph_y_query()

    def_graph_title_and_key(self):
        ifself.use_opportunitiesandself._context.get('in_sales_app'):
            return['',_('Sales:UntaxedTotal')]
        returnsuper(CrmTeam,self)._graph_title_and_key()
    
    def_extra_sql_conditions(self):
        ifself.use_opportunitiesandself._context.get('in_sales_app'):
            return"ANDstatein('sale','done','pos_done')"
        returnsuper(CrmTeam,self)._extra_sql_conditions()
