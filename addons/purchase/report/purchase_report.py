#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

#
#Pleasenotethatthesereportsarenotmulti-currency!!!
#

importre

fromflectraimportapi,fields,models,tools
fromflectra.exceptionsimportUserError
fromflectra.osv.expressionimportAND,expression


classPurchaseReport(models.Model):
    _name="purchase.report"
    _description="PurchaseReport"
    _auto=False
    _order='date_orderdesc,price_totaldesc'

    date_order=fields.Datetime('OrderDate',readonly=True,help="DepictsthedatewhentheQuotationshouldbevalidatedandconvertedintoapurchaseorder.")
    state=fields.Selection([
        ('draft','DraftRFQ'),
        ('sent','RFQSent'),
        ('toapprove','ToApprove'),
        ('purchase','PurchaseOrder'),
        ('done','Done'),
        ('cancel','Cancelled')
    ],'Status',readonly=True)
    product_id=fields.Many2one('product.product','Product',readonly=True)
    partner_id=fields.Many2one('res.partner','Vendor',readonly=True)
    date_approve=fields.Datetime('ConfirmationDate',readonly=True)
    product_uom=fields.Many2one('uom.uom','ReferenceUnitofMeasure',required=True)
    company_id=fields.Many2one('res.company','Company',readonly=True)
    currency_id=fields.Many2one('res.currency','Currency',readonly=True)
    user_id=fields.Many2one('res.users','PurchaseRepresentative',readonly=True)
    delay=fields.Float('DaystoConfirm',digits=(16,2),readonly=True,group_operator='avg',help="Amountoftimebetweenpurchaseapprovalandorderbydate.")
    delay_pass=fields.Float('DaystoReceive',digits=(16,2),readonly=True,group_operator='avg',
                              help="Amountoftimebetweendateplannedandorderbydateforeachpurchaseorderline.")
    avg_days_to_purchase=fields.Float(
        'AverageDaystoPurchase',digits=(16,2),readonly=True,store=False, #needsstore=Falsetopreventshowingupasa'measure'option
        help="Amountoftimebetweenpurchaseapprovalanddocumentcreationdate.Duetoahackneededtocalculatethis,\
              everyrecordwillshowthesameaveragevalue,thereforeonlyusethisasanaggregatedvaluewithgroup_operator=avg")
    price_total=fields.Float('Total',readonly=True)
    price_average=fields.Float('AverageCost',readonly=True,group_operator="avg")
    nbr_lines=fields.Integer('#ofLines',readonly=True)
    category_id=fields.Many2one('product.category','ProductCategory',readonly=True)
    product_tmpl_id=fields.Many2one('product.template','ProductTemplate',readonly=True)
    country_id=fields.Many2one('res.country','PartnerCountry',readonly=True)
    fiscal_position_id=fields.Many2one('account.fiscal.position',string='FiscalPosition',readonly=True)
    account_analytic_id=fields.Many2one('account.analytic.account','AnalyticAccount',readonly=True)
    commercial_partner_id=fields.Many2one('res.partner','CommercialEntity',readonly=True)
    weight=fields.Float('GrossWeight',readonly=True)
    volume=fields.Float('Volume',readonly=True)
    order_id=fields.Many2one('purchase.order','Order',readonly=True)
    untaxed_total=fields.Float('UntaxedTotal',readonly=True)
    qty_ordered=fields.Float('QtyOrdered',readonly=True)
    qty_received=fields.Float('QtyReceived',readonly=True)
    qty_billed=fields.Float('QtyBilled',readonly=True)
    qty_to_be_billed=fields.Float('QtytobeBilled',readonly=True)

    @property
    def_table_query(self):
        '''Reportneedstobedynamictotakeintoaccountmulti-companyselected+multi-currencyrates'''
        return'%s%s%s%s'%(self._select(),self._from(),self._where(),self._group_by())

    def_select(self):
        select_str="""
                SELECT
                    po.idasorder_id,
                    min(l.id)asid,
                    po.date_orderasdate_order,
                    po.state,
                    po.date_approve,
                    po.dest_address_id,
                    po.partner_idaspartner_id,
                    po.user_idasuser_id,
                    po.company_idascompany_id,
                    po.fiscal_position_idasfiscal_position_id,
                    l.product_id,
                    p.product_tmpl_id,
                    t.categ_idascategory_id,
                    po.currency_id,
                    t.uom_idasproduct_uom,
                    extract(epochfromage(po.date_approve,po.date_order))/(24*60*60)::decimal(16,2)asdelay,
                    extract(epochfromage(l.date_planned,po.date_order))/(24*60*60)::decimal(16,2)asdelay_pass,
                    count(*)asnbr_lines,
                    sum(l.price_total/COALESCE(po.currency_rate,1.0))::decimal(16,2)*currency_table.rateasprice_total,
                    (sum(l.product_qty*l.price_unit/COALESCE(po.currency_rate,1.0))/NULLIF(sum(l.product_qty/line_uom.factor*product_uom.factor),0.0))::decimal(16,2)*currency_table.rateasprice_average,
                    partner.country_idascountry_id,
                    partner.commercial_partner_idascommercial_partner_id,
                    analytic_account.idasaccount_analytic_id,
                    sum(p.weight*l.product_qty/line_uom.factor*product_uom.factor)asweight,
                    sum(p.volume*l.product_qty/line_uom.factor*product_uom.factor)asvolume,
                    sum(l.price_subtotal/COALESCE(po.currency_rate,1.0))::decimal(16,2)*currency_table.rateasuntaxed_total,
                    sum(l.product_qty/line_uom.factor*product_uom.factor)asqty_ordered,
                    sum(l.qty_received/line_uom.factor*product_uom.factor)asqty_received,
                    sum(l.qty_invoiced/line_uom.factor*product_uom.factor)asqty_billed,
                    casewhent.purchase_method='purchase'
                         thensum(l.product_qty/line_uom.factor*product_uom.factor)-sum(l.qty_invoiced/line_uom.factor*product_uom.factor)
                         elsesum(l.qty_received/line_uom.factor*product_uom.factor)-sum(l.qty_invoiced/line_uom.factor*product_uom.factor)
                    endasqty_to_be_billed
        """
        returnselect_str

    def_from(self):
        from_str="""
            FROM
            purchase_order_linel
                joinpurchase_orderpoon(l.order_id=po.id)
                joinres_partnerpartneronpo.partner_id=partner.id
                    leftjoinproduct_productpon(l.product_id=p.id)
                        leftjoinproduct_templateton(p.product_tmpl_id=t.id)
                leftjoinuom_uomline_uomon(line_uom.id=l.product_uom)
                leftjoinuom_uomproduct_uomon(product_uom.id=t.uom_id)
                leftjoinaccount_analytic_accountanalytic_accounton(l.account_analytic_id=analytic_account.id)
                leftjoin{currency_table}ONcurrency_table.company_id=po.company_id
        """.format(
            currency_table=self.env['res.currency']._get_query_currency_table({'multi_company':True,'date':{'date_to':fields.Date.today()}}),
        )
        returnfrom_str

    def_where(self):
        return"""
            WHERE
                l.display_typeISNULL
        """

    def_group_by(self):
        group_by_str="""
            GROUPBY
                po.company_id,
                po.user_id,
                po.partner_id,
                line_uom.factor,
                po.currency_id,
                l.price_unit,
                po.date_approve,
                l.date_planned,
                l.product_uom,
                po.dest_address_id,
                po.fiscal_position_id,
                l.product_id,
                p.product_tmpl_id,
                t.categ_id,
                po.date_order,
                po.state,
                line_uom.uom_type,
                line_uom.category_id,
                t.uom_id,
                t.purchase_method,
                line_uom.id,
                product_uom.factor,
                partner.country_id,
                partner.commercial_partner_id,
                analytic_account.id,
                po.id,
                currency_table.rate
        """
        returngroup_by_str

    @api.model
    defread_group(self,domain,fields,groupby,offset=0,limit=None,orderby=False,lazy=True):
        """ThisisahacktoallowustocorrectlycalculatetheaverageofPOspecificdatevaluessince
            thenormalreportqueryresultwillduplicatePOvaluesacrossitsPOlinesduringjoinsand
            leadtoincorrectaggregationvalues.

            OnlytheAVGoperatorissupportedforavg_days_to_purchase.
        """
        avg_days_to_purchase=next((fieldforfieldinfieldsifre.search(r'\bavg_days_to_purchase\b',field)),False)

        ifavg_days_to_purchase:
            fields.remove(avg_days_to_purchase)
            ifany(field.split(':')[1].split('(')[0]!='avg'forfieldin[avg_days_to_purchase]iffield):
                raiseUserError("Value:'avg_days_to_purchase'shouldonlybeusedtoshowanaverage.Ifyouareseeingthismessagethenitisbeingaccessedincorrectly.")

        if'price_average:avg'infields:
            fields.extend(['aggregated_qty_ordered:array_agg(qty_ordered)'])
            fields.extend(['aggregated_price_average:array_agg(price_average)'])

        res=[]
        iffields:
            res=super(PurchaseReport,self).read_group(domain,fields,groupby,offset=offset,limit=limit,orderby=orderby,lazy=lazy)

        if'price_average:avg'infields:
            qties='aggregated_qty_ordered'
            special_field='aggregated_price_average'
            fordatainres:
                ifdata[special_field]anddata[qties]:
                    total_unit_cost=sum(float(value)*float(qty)forvalue,qtyinzip(data[special_field],data[qties])ifqtyandvalue)
                    total_qty_ordered=sum(float(qty)forqtyindata[qties]ifqty)
                    data['price_average']=(total_unit_cost/total_qty_ordered)iftotal_qty_orderedelse0
                deldata[special_field]
                deldata[qties]
        ifnotresandavg_days_to_purchase:
            res=[{}]

        ifavg_days_to_purchase:
            self.check_access_rights('read')
            query="""SELECTAVG(days_to_purchase.po_days_to_purchase)::decimal(16,2)ASavg_days_to_purchase
                          FROM(
                              SELECTextract(epochfromage(po.date_approve,po.create_date))/(24*60*60)ASpo_days_to_purchase
                              FROMpurchase_orderpo
                              WHEREpo.idIN(
                                  SELECT"purchase_report"."order_id"FROM%sWHERE%s)
                              )ASdays_to_purchase
                    """

            subdomain=AND([domain,[('company_id','=',self.env.company.id),('date_approve','!=',False)]])
            subtables,subwhere,subparams=expression(subdomain,self).query.get_sql()

            self.env.cr.execute(query%(subtables,subwhere),subparams)
            res[0].update({
                '__count':1,
                avg_days_to_purchase.split(':')[0]:self.env.cr.fetchall()[0][0],
            })
        returnres
