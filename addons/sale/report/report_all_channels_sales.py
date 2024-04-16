#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,tools


classPosSaleReport(models.Model):
    _name="report.all.channels.sales"
    _description="SalesbyChannel(AllinOne)"
    _auto=False

    name=fields.Char('OrderReference',readonly=True)
    partner_id=fields.Many2one('res.partner','Partner',readonly=True)
    product_id=fields.Many2one('product.product',string='Product',readonly=True)
    product_tmpl_id=fields.Many2one('product.template','ProductTemplate',readonly=True)
    date_order=fields.Datetime(string='DateOrder',readonly=True)
    user_id=fields.Many2one('res.users','Salesperson',readonly=True)
    categ_id=fields.Many2one('product.category','ProductCategory',readonly=True)
    company_id=fields.Many2one('res.company','Company',readonly=True)
    price_total=fields.Float('Total',readonly=True)
    pricelist_id=fields.Many2one('product.pricelist','Pricelist',readonly=True)
    country_id=fields.Many2one('res.country','PartnerCountry',readonly=True)
    price_subtotal=fields.Float(string='PriceSubtotal',readonly=True)
    product_qty=fields.Float('ProductQuantity',readonly=True)
    analytic_account_id=fields.Many2one('account.analytic.account','AnalyticAccount',readonly=True)
    team_id=fields.Many2one('crm.team','SalesTeam',readonly=True)

    def_so(self):
        so_str="""
                SELECTsol.idASid,
                    so.nameASname,
                    so.partner_idASpartner_id,
                    sol.product_idASproduct_id,
                    pro.product_tmpl_idASproduct_tmpl_id,
                    so.date_orderASdate_order,
                    so.user_idASuser_id,
                    pt.categ_idAScateg_id,
                    so.company_idAScompany_id,
                    sol.price_total/CASECOALESCE(so.currency_rate,0)WHEN0THEN1.0ELSEso.currency_rateENDASprice_total,
                    so.pricelist_idASpricelist_id,
                    rp.country_idAScountry_id,
                    sol.price_subtotal/CASECOALESCE(so.currency_rate,0)WHEN0THEN1.0ELSEso.currency_rateENDASprice_subtotal,
                    (sol.product_uom_qty/u.factor*u2.factor)asproduct_qty,
                    so.analytic_account_idASanalytic_account_id,
                    so.team_idASteam_id

            FROMsale_order_linesol
                    JOINsale_ordersoON(sol.order_id=so.id)
                    LEFTJOINproduct_productproON(sol.product_id=pro.id)
                    JOINres_partnerrpON(so.partner_id=rp.id)
                    LEFTJOINproduct_templateptON(pro.product_tmpl_id=pt.id)
                    LEFTJOINproduct_pricelistppON(so.pricelist_id=pp.id)
                    LEFTJOINuom_uomuon(u.id=sol.product_uom)
                    LEFTJOINuom_uomu2on(u2.id=pt.uom_id)
            WHEREso.statein('sale','done')
        """
        returnso_str

    def_from(self):
        return"""(%s)"""%(self._so())

    def_get_main_request(self):
        request="""
            CREATEorREPLACEVIEW%sAS
                SELECTidASid,
                    name,
                    partner_id,
                    product_id,
                    product_tmpl_id,
                    date_order,
                    user_id,
                    categ_id,
                    company_id,
                    price_total,
                    pricelist_id,
                    analytic_account_id,
                    country_id,
                    team_id,
                    price_subtotal,
                    product_qty
                FROM%s
                ASfoo"""%(self._table,self._from())
        returnrequest

    definit(self):
        tools.drop_view_if_exists(self.env.cr,self._table)
        self.env.cr.execute(self._get_main_request())
