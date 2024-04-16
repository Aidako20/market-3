#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporttools
fromflectraimportapi,fields,models


classSaleReport(models.Model):
    _inherit="sale.report"

    @api.model
    def_get_done_states(self):
        done_states=super(SaleReport,self)._get_done_states()
        done_states.extend(['pos_done','invoiced'])
        returndone_states

    state=fields.Selection(selection_add=[('pos_draft','New'),
                                            ('paid','Paid'),
                                            ('pos_done','Posted'),
                                            ('invoiced','Invoiced')],string='Status',readonly=True)

    def_select_pos(self,fields=None):
        ifnotfields:
            fields={}
        select_='''
            -MIN(l.id)ASid,
            l.product_idASproduct_id,
            t.uom_idASproduct_uom,
            sum(l.qty)ASproduct_uom_qty,
            sum(l.qty)ASqty_delivered,
            CASEWHENpos.state='invoiced'THENsum(l.qty)ELSE0ENDASqty_invoiced,
            CASEWHENpos.state!='invoiced'THENsum(l.qty)ELSE0ENDASqty_to_invoice,
            SUM(l.price_subtotal_incl)/MIN(CASECOALESCE(pos.currency_rate,0)WHEN0THEN1.0ELSEpos.currency_rateEND)ASprice_total,
            SUM(l.price_subtotal)/MIN(CASECOALESCE(pos.currency_rate,0)WHEN0THEN1.0ELSEpos.currency_rateEND)ASprice_subtotal,
            (CASEWHENpos.state!='invoiced'THENSUM(l.price_subtotal)ELSE0END)/MIN(CASECOALESCE(pos.currency_rate,0)WHEN0THEN1.0ELSEpos.currency_rateEND)ASamount_to_invoice,
            (CASEWHENpos.state='invoiced'THENSUM(l.price_subtotal)ELSE0END)/MIN(CASECOALESCE(pos.currency_rate,0)WHEN0THEN1.0ELSEpos.currency_rateEND)ASamount_invoiced,
            count(*)ASnbr,
            pos.nameASname,
            pos.date_orderASdate,
            CASEWHENpos.state='draft'THEN'pos_draft'WHENpos.state='done'THEN'pos_done'elsepos.stateENDASstate,
            pos.partner_idASpartner_id,
            pos.user_idASuser_id,
            pos.company_idAScompany_id,
            NULLAScampaign_id,
            NULLASmedium_id,
            NULLASsource_id,
            extract(epochfromavg(date_trunc('day',pos.date_order)-date_trunc('day',pos.create_date)))/(24*60*60)::decimal(16,2)ASdelay,
            t.categ_idAScateg_id,
            pos.pricelist_idASpricelist_id,
            NULLASanalytic_account_id,
            pos.crm_team_idASteam_id,
            p.product_tmpl_id,
            partner.country_idAScountry_id,
            partner.industry_idASindustry_id,
            partner.commercial_partner_idAScommercial_partner_id,
            (sum(p.weight)*l.qty/u.factor)ASweight,
            (sum(p.volume)*l.qty/u.factor)ASvolume,
            l.discountasdiscount,
            sum((l.price_unit*l.discount*l.qty/100.0/CASECOALESCE(pos.currency_rate,0)WHEN0THEN1.0ELSEpos.currency_rateEND))asdiscount_amount,
            NULLasorder_id
        '''

        forfieldinfields.keys():
            select_+=',NULLAS%s'%(field)
        returnselect_

    def_from_pos(self):
        from_='''
            pos_order_linel
                  joinpos_orderposon(l.order_id=pos.id)
                  leftjoinres_partnerpartnerON(pos.partner_id=partner.idORpos.partner_id=NULL)
                    leftjoinproduct_productpon(l.product_id=p.id)
                    leftjoinproduct_templateton(p.product_tmpl_id=t.id)
                    LEFTJOINuom_uomuON(u.id=t.uom_id)
                    LEFTJOINpos_sessionsessionON(session.id=pos.session_id)
                    LEFTJOINpos_configconfigON(config.id=session.config_id)
                leftjoinproduct_pricelistppon(pos.pricelist_id=pp.id)
        '''
        returnfrom_

    def_group_by_pos(self):
        groupby_='''
            l.order_id,
            l.product_id,
            l.price_unit,
            l.discount,
            l.qty,
            t.uom_id,
            t.categ_id,
            pos.name,
            pos.date_order,
            pos.partner_id,
            pos.user_id,
            pos.state,
            pos.company_id,
            pos.pricelist_id,
            p.product_tmpl_id,
            partner.country_id,
            partner.industry_id,
            partner.commercial_partner_id,
            u.factor,
            pos.crm_team_id
        '''
        returngroupby_

    def_query(self,with_clause='',fields=None,groupby='',from_clause=''):
        ifnotfields:
            fields={}
        res=super()._query(with_clause,fields,groupby,from_clause)
        sale_fields=self._select_additional_fields(fields)
        current='(SELECT%sFROM%sGROUPBY%s)'%\
                  (self._select_pos(sale_fields),self._from_pos(),self._group_by_pos())

        return'%sUNIONALL%s'%(res,current)
