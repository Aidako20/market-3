#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importre

fromflectraimportapi,fields,models
fromflectra.exceptionsimportUserError
fromflectra.osv.expressionimportexpression


classPurchaseReport(models.Model):
    _inherit="purchase.report"

    picking_type_id=fields.Many2one('stock.warehouse','Warehouse',readonly=True)
    avg_receipt_delay=fields.Float(
        'AverageReceiptDelay',digits=(16,2),readonly=True,store=False, #needsstore=Falsetopreventshowingupasa'measure'option
        help="Amountoftimebetweenexpectedandeffectivereceiptdate.Duetoahackneededtocalculatethis,\
              everyrecordwillshowthesameaveragevalue,thereforeonlyusethisasanaggregatedvaluewithgroup_operator=avg")
    effective_date=fields.Datetime(string="EffectiveDate")

    def_select(self):
        returnsuper(PurchaseReport,self)._select()+",spt.warehouse_idaspicking_type_id,po.effective_dateaseffective_date"

    def_from(self):
        returnsuper(PurchaseReport,self)._from()+"leftjoinstock_picking_typespton(spt.id=po.picking_type_id)"

    def_group_by(self):
        returnsuper(PurchaseReport,self)._group_by()+",spt.warehouse_id,effective_date"

    @api.model
    defread_group(self,domain,fields,groupby,offset=0,limit=None,orderby=False,lazy=True):
        """ThisisahacktoallowustocorrectlycalculatetheaverageofPOspecificdatevaluessince
            thenormalreportqueryresultwillduplicatePOvaluesacrossitsPOlinesduringjoinsand
            leadtoincorrectaggregationvalues.

            OnlytheAVGoperatorissupportedforavg_receipt_delay.
        """
        avg_receipt_delay=next((fieldforfieldinfieldsifre.search(r'\bavg_receipt_delay\b',field)),False)

        ifavg_receipt_delay:
            fields.remove(avg_receipt_delay)
            ifany(field.split(':')[1].split('(')[0]!='avg'forfieldin[avg_receipt_delay]iffield):
                raiseUserError("Value:'avg_receipt_delay'shouldonlybeusedtoshowanaverage.Ifyouareseeingthismessagethenitisbeingaccessedincorrectly.")

        res=[]
        iffields:
            res=super(PurchaseReport,self).read_group(domain,fields,groupby,offset=offset,limit=limit,orderby=orderby,lazy=lazy)

        ifnotresandavg_receipt_delay:
            res=[{}]

        ifavg_receipt_delay:
            query="""SELECTAVG(receipt_delay.po_receipt_delay)::decimal(16,2)ASavg_receipt_delay
                          FROM(
                              SELECTextract(epochfromage(po.effective_date,po.date_planned))/(24*60*60)ASpo_receipt_delay
                              FROMpurchase_orderpo
                              WHEREpo.idIN(
                                  SELECT"purchase_report"."order_id"FROM%sWHERE%s)
                              )ASreceipt_delay
                    """

            subdomain=domain+[('company_id','=',self.env.company.id),('effective_date','!=',False)]
            subtables,subwhere,subparams=expression(subdomain,self).query.get_sql()

            self.env.cr.execute(query%(subtables,subwhere),subparams)
            res[0].update({
                '__count':1,
                avg_receipt_delay.split(':')[0]:self.env.cr.fetchall()[0][0],
            })
        returnres
