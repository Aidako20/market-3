#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdate

fromflectraimportapi,fields,models,_


classCrmTeam(models.Model):
    _inherit='crm.team'

    use_quotations=fields.Boolean(string='Quotations',help="Checkthisboxifyousendquotationstoyourcustomersratherthanconfirmingordersstraightaway.")
    invoiced=fields.Float(
        compute='_compute_invoiced',
        string='InvoicedThisMonth',readonly=True,
        help="Invoicerevenueforthecurrentmonth.Thisistheamountthesales"
                "channelhasinvoicedthismonth.Itisusedtocomputetheprogressionratio"
                "ofthecurrentandtargetrevenueonthekanbanview.")
    invoiced_target=fields.Float(
        string='InvoicingTarget',
        help="Revenuetargetforthecurrentmonth(untaxedtotalofconfirmedinvoices).")
    quotations_count=fields.Integer(
        compute='_compute_quotations_to_invoice',
        string='Numberofquotationstoinvoice',readonly=True)
    quotations_amount=fields.Float(
        compute='_compute_quotations_to_invoice',
        string='Amountofquotationstoinvoice',readonly=True)
    sales_to_invoice_count=fields.Integer(
        compute='_compute_sales_to_invoice',
        string='Numberofsalestoinvoice',readonly=True)


    def_compute_quotations_to_invoice(self):
        query=self.env['sale.order']._where_calc([
            ('team_id','in',self.ids),
            ('state','in',['draft','sent']),
        ])
        self.env['sale.order']._apply_ir_rules(query,'read')
        _,where_clause,where_clause_args=query.get_sql()
        select_query="""
            SELECTteam_id,count(*),sum(amount_total/
                CASECOALESCE(currency_rate,0)
                WHEN0THEN1.0
                ELSEcurrency_rate
                END
            )asamount_total
            FROMsale_order
            WHERE%s
            GROUPBYteam_id
        """%where_clause
        self.env.cr.execute(select_query,where_clause_args)
        quotation_data=self.env.cr.dictfetchall()
        teams=self.browse()
        fordatuminquotation_data:
            team=self.browse(datum['team_id'])
            team.quotations_amount=datum['amount_total']
            team.quotations_count=datum['count']
            teams|=team
        remaining=(self-teams)
        remaining.quotations_amount=0
        remaining.quotations_count=0

    def_compute_sales_to_invoice(self):
        sale_order_data=self.env['sale.order'].read_group([
            ('team_id','in',self.ids),
            ('invoice_status','=','toinvoice'),
        ],['team_id'],['team_id'])
        data_map={datum['team_id'][0]:datum['team_id_count']fordatuminsale_order_data}
        forteaminself:
            team.sales_to_invoice_count=data_map.get(team.id,0.0)

    def_compute_invoiced(self):
        ifnotself:
            return

        query='''
            SELECT
                move.team_idASteam_id,
                SUM(move.amount_untaxed_signed)ASamount_untaxed_signed
            FROMaccount_movemove
            WHEREmove.move_typeIN('out_invoice','out_refund','out_receipt')
            ANDmove.payment_stateIN('in_payment','paid','reversed')
            ANDmove.state='posted'
            ANDmove.team_idIN%s
            ANDmove.dateBETWEEN%sAND%s
            GROUPBYmove.team_id
        '''
        today=fields.Date.today()
        params=[tuple(self.ids),fields.Date.to_string(today.replace(day=1)),fields.Date.to_string(today)]
        self._cr.execute(query,params)

        data_map=dict((v[0],v[1])forvinself._cr.fetchall())
        forteaminself:
            team.invoiced=data_map.get(team.id,0.0)

    def_graph_get_model(self):
        ifself._context.get('in_sales_app'):
            return'sale.report'
        returnsuper(CrmTeam,self)._graph_get_model()

    def_graph_date_column(self):
        ifself._context.get('in_sales_app'):
            return'date'
        returnsuper(CrmTeam,self)._graph_date_column()

    def_graph_y_query(self):
        ifself._context.get('in_sales_app'):
            return'SUM(price_subtotal)'
        returnsuper(CrmTeam,self)._graph_y_query()

    def_extra_sql_conditions(self):
        ifself._context.get('in_sales_app'):
            return"ANDstatein('sale','done','pos_done')"
        returnsuper(CrmTeam,self)._extra_sql_conditions()

    def_graph_title_and_key(self):
        ifself._context.get('in_sales_app'):
            return['',_('Sales:UntaxedTotal')]#nomoretitle
        returnsuper(CrmTeam,self)._graph_title_and_key()

    def_compute_dashboard_button_name(self):
        super(CrmTeam,self)._compute_dashboard_button_name()
        ifself._context.get('in_sales_app'):
            self.update({'dashboard_button_name':_("SalesAnalysis")})

    defaction_primary_channel_button(self):
        ifself._context.get('in_sales_app'):
            returnself.env["ir.actions.actions"]._for_xml_id("sale.action_order_report_so_salesteam")
        returnsuper(CrmTeam,self).action_primary_channel_button()

    defupdate_invoiced_target(self,value):
        returnself.write({'invoiced_target':round(float(valueor0))})
