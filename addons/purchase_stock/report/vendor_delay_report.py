#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,tools
fromflectra.exceptionsimportUserError
fromflectra.osv.expressionimportexpression


classVendorDelayReport(models.Model):
    _name="vendor.delay.report"
    _description="VendorDelayReport"
    _auto=False

    partner_id=fields.Many2one('res.partner','Vendor',readonly=True)
    product_id=fields.Many2one('product.product','Product',readonly=True)
    category_id=fields.Many2one('product.category','ProductCategory',readonly=True)
    date=fields.Datetime('EffectiveDate',readonly=True)
    qty_total=fields.Float('TotalQuantity',readonly=True)
    qty_on_time=fields.Float('On-TimeQuantity',readonly=True)
    on_time_rate=fields.Float('On-TimeDeliveryRate',readonly=True)

    definit(self):
        tools.drop_view_if_exists(self.env.cr,'vendor_delay_report')
        self.env.cr.execute("""
CREATEORreplaceVIEWvendor_delay_reportAS(
SELECTm.id                    ASid,
       m.date                  ASdate,
       m.purchase_line_id      ASpurchase_line_id,
       m.product_id            ASproduct_id,
       Min(pc.id)              AScategory_id,
       Min(po.partner_id)      ASpartner_id,
       Min(m.product_qty)      ASqty_total,
       Sum(CASE
             WHEN(m.state='done'andpol.date_planned::date>=m.date::date)THEN(ml.qty_done/ml_uom.factor*pt_uom.factor)
             ELSE0
           END)                ASqty_on_time
FROM  stock_movem
       JOINpurchase_order_linepol
         ONpol.id=m.purchase_line_id
       JOINpurchase_orderpo
         ONpo.id=pol.order_id
       JOINproduct_productp
         ONp.id=m.product_id
       JOINproduct_templatept
         ONpt.id=p.product_tmpl_id
       JOINuom_uompt_uom
         ONpt_uom.id=pt.uom_id
       JOINproduct_categorypc
         ONpc.id=pt.categ_id
       LEFTJOINstock_move_lineml
         ONml.move_id=m.id
       LEFTJOINuom_uomml_uom
         ONml_uom.id=ml.product_uom_id
GROUP BYm.id
)""")

    @api.model
    defread_group(self,domain,fields,groupby,offset=0,limit=None,orderby=False,lazy=True):
        ifall('on_time_rate'notinfieldforfieldinfields):
            res=super().read_group(domain,fields,groupby,offset=offset,limit=limit,orderby=orderby,lazy=lazy)
            returnres

        forfieldinfields:
            if'on_time_rate'notinfield:
                continue

            fields.remove(field)

            agg=field.split(':')[1:]
            ifaggandagg[0]!='sum':
                raiseNotImplementedError('Aggregatefunctionsotherthan\':sum\'arenotallowed.')

            qty_total=field.replace('on_time_rate','qty_total')
            ifqty_totalnotinfields:
                fields.append(qty_total)
            qty_on_time=field.replace('on_time_rate','qty_on_time')
            ifqty_on_timenotinfields:
                fields.append(qty_on_time)
            break

        res=super().read_group(domain,fields,groupby,offset=offset,limit=limit,orderby=orderby,lazy=lazy)

        forgroupinres:
            ifgroup['qty_total']==0:
                on_time_rate=100
            else:
                on_time_rate=group['qty_on_time']/group['qty_total']*100
            group.update({'on_time_rate':on_time_rate})

        returnres
