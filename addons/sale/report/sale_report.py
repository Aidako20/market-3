#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporttools
fromflectraimportapi,fields,models


classSaleReport(models.Model):
    _name="sale.report"
    _description="SalesAnalysisReport"
    _auto=False
    _rec_name='date'
    _order='datedesc'

    @api.model
    def_get_done_states(self):
        return['sale','done','paid']

    name=fields.Char('OrderReference',readonly=True)
    date=fields.Datetime('OrderDate',readonly=True)
    product_id=fields.Many2one('product.product','ProductVariant',readonly=True)
    product_uom=fields.Many2one('uom.uom','UnitofMeasure',readonly=True)
    product_uom_qty=fields.Float('QtyOrdered',readonly=True)
    qty_delivered=fields.Float('QtyDelivered',readonly=True)
    qty_to_invoice=fields.Float('QtyToInvoice',readonly=True)
    qty_invoiced=fields.Float('QtyInvoiced',readonly=True)
    partner_id=fields.Many2one('res.partner','Customer',readonly=True)
    company_id=fields.Many2one('res.company','Company',readonly=True)
    user_id=fields.Many2one('res.users','Salesperson',readonly=True)
    price_total=fields.Float('Total',readonly=True)
    price_subtotal=fields.Float('UntaxedTotal',readonly=True)
    untaxed_amount_to_invoice=fields.Float('UntaxedAmountToInvoice',readonly=True)
    untaxed_amount_invoiced=fields.Float('UntaxedAmountInvoiced',readonly=True)
    product_tmpl_id=fields.Many2one('product.template','Product',readonly=True)
    categ_id=fields.Many2one('product.category','ProductCategory',readonly=True)
    nbr=fields.Integer('#ofLines',readonly=True)
    pricelist_id=fields.Many2one('product.pricelist','Pricelist',readonly=True)
    analytic_account_id=fields.Many2one('account.analytic.account','AnalyticAccount',readonly=True)
    team_id=fields.Many2one('crm.team','SalesTeam',readonly=True)
    country_id=fields.Many2one('res.country','CustomerCountry',readonly=True)
    industry_id=fields.Many2one('res.partner.industry','CustomerIndustry',readonly=True)
    commercial_partner_id=fields.Many2one('res.partner','CustomerEntity',readonly=True)
    state=fields.Selection([
        ('draft','DraftQuotation'),
        ('sent','QuotationSent'),
        ('sale','SalesOrder'),
        ('done','SalesDone'),
        ('cancel','Cancelled'),
        ],string='Status',readonly=True)
    weight=fields.Float('GrossWeight',readonly=True)
    volume=fields.Float('Volume',readonly=True)

    discount=fields.Float('Discount%',readonly=True)
    discount_amount=fields.Float('DiscountAmount',readonly=True)
    campaign_id=fields.Many2one('utm.campaign','Campaign')
    medium_id=fields.Many2one('utm.medium','Medium')
    source_id=fields.Many2one('utm.source','Source')

    order_id=fields.Many2one('sale.order','Order#',readonly=True)

    def_select_sale(self,fields=None):
        ifnotfields:
            fields={}
        select_="""
            coalesce(min(l.id),-s.id)asid,
            l.product_idasproduct_id,
            t.uom_idasproduct_uom,
            CASEWHENl.product_idISNOTNULLTHENsum(l.product_uom_qty/u.factor*u2.factor)ELSE0ENDasproduct_uom_qty,
            CASEWHENl.product_idISNOTNULLTHENsum(l.qty_delivered/u.factor*u2.factor)ELSE0ENDasqty_delivered,
            CASEWHENl.product_idISNOTNULLTHENsum(l.qty_invoiced/u.factor*u2.factor)ELSE0ENDasqty_invoiced,
            CASEWHENl.product_idISNOTNULLTHENsum(l.qty_to_invoice/u.factor*u2.factor)ELSE0ENDasqty_to_invoice,
            CASEWHENl.product_idISNOTNULLTHENsum(l.price_total/CASECOALESCE(s.currency_rate,0)WHEN0THEN1.0ELSEs.currency_rateEND)ELSE0ENDasprice_total,
            CASEWHENl.product_idISNOTNULLTHENsum(l.price_subtotal/CASECOALESCE(s.currency_rate,0)WHEN0THEN1.0ELSEs.currency_rateEND)ELSE0ENDasprice_subtotal,
            CASEWHENl.product_idISNOTNULLTHENsum(l.untaxed_amount_to_invoice/CASECOALESCE(s.currency_rate,0)WHEN0THEN1.0ELSEs.currency_rateEND)ELSE0ENDasuntaxed_amount_to_invoice,
            CASEWHENl.product_idISNOTNULLTHENsum(l.untaxed_amount_invoiced/CASECOALESCE(s.currency_rate,0)WHEN0THEN1.0ELSEs.currency_rateEND)ELSE0ENDasuntaxed_amount_invoiced,
            count(*)asnbr,
            s.nameasname,
            s.date_orderasdate,
            s.stateasstate,
            s.partner_idaspartner_id,
            s.user_idasuser_id,
            s.company_idascompany_id,
            s.campaign_idascampaign_id,
            s.medium_idasmedium_id,
            s.source_idassource_id,
            extract(epochfromavg(date_trunc('day',s.date_order)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2)asdelay,
            t.categ_idascateg_id,
            s.pricelist_idaspricelist_id,
            s.analytic_account_idasanalytic_account_id,
            s.team_idasteam_id,
            p.product_tmpl_id,
            partner.country_idascountry_id,
            partner.industry_idasindustry_id,
            partner.commercial_partner_idascommercial_partner_id,
            CASEWHENl.product_idISNOTNULLTHENsum(p.weight*l.product_uom_qty/u.factor*u2.factor)ELSE0ENDasweight,
            CASEWHENl.product_idISNOTNULLTHENsum(p.volume*l.product_uom_qty/u.factor*u2.factor)ELSE0ENDasvolume,
            l.discountasdiscount,
            CASEWHENl.product_idISNOTNULLTHENsum((l.price_unit*l.product_uom_qty*l.discount/100.0/CASECOALESCE(s.currency_rate,0)WHEN0THEN1.0ELSEs.currency_rateEND))ELSE0ENDasdiscount_amount,
            s.idasorder_id
        """

        forfieldinfields.values():
            select_+=field
        returnselect_

    def_from_sale(self,from_clause=''):
        from_="""
                sale_order_linel
                      rightouterjoinsale_orderson(s.id=l.order_id)
                      joinres_partnerpartnerons.partner_id=partner.id
                        leftjoinproduct_productpon(l.product_id=p.id)
                            leftjoinproduct_templateton(p.product_tmpl_id=t.id)
                    leftjoinuom_uomuon(u.id=l.product_uom)
                    leftjoinuom_uomu2on(u2.id=t.uom_id)
                    leftjoinproduct_pricelistppon(s.pricelist_id=pp.id)
                %s
        """%from_clause
        returnfrom_

    def_group_by_sale(self,groupby=''):
        groupby_="""
            l.product_id,
            l.order_id,
            t.uom_id,
            t.categ_id,
            s.name,
            s.date_order,
            s.partner_id,
            s.user_id,
            s.state,
            s.company_id,
            s.campaign_id,
            s.medium_id,
            s.source_id,
            s.pricelist_id,
            s.analytic_account_id,
            s.team_id,
            p.product_tmpl_id,
            partner.country_id,
            partner.industry_id,
            partner.commercial_partner_id,
            l.discount,
            s.id%s
        """%(groupby)
        returngroupby_

    def_select_additional_fields(self,fields):
        """HooktoreturnadditionalfieldsSQLspecificationforselectpartofthetablequery.

        :paramdictfields:additionalfieldsinfoprovidedby_queryoverrides(oldAPI),preferoverriding
            _select_additional_fieldsinstead.
        :returns:mappingfield->SQLcomputationofthefield
        :rtype:dict
        """
        returnfields

    def_query(self,with_clause='',fields=None,groupby='',from_clause=''):
        ifnotfields:
            fields={}
        sale_report_fields=self._select_additional_fields(fields)
        with_=("WITH%s"%with_clause)ifwith_clauseelse""
        return'%s(SELECT%sFROM%sWHEREl.display_typeISNULLGROUPBY%s)'%\
               (with_,self._select_sale(sale_report_fields),self._from_sale(from_clause),self._group_by_sale(groupby))

    definit(self):
        #self._table=sale_report
        tools.drop_view_if_exists(self.env.cr,self._table)
        self.env.cr.execute("""CREATEorREPLACEVIEW%sas(%s)"""%(self._table,self._query()))

classSaleOrderReportProforma(models.AbstractModel):
    _name='report.sale.report_saleproforma'
    _description='ProformaReport'

    @api.model
    def_get_report_values(self,docids,data=None):
        docs=self.env['sale.order'].browse(docids)
        return{
            'doc_ids':docs.ids,
            'doc_model':'sale.order',
            'docs':docs,
            'proforma':True
        }
