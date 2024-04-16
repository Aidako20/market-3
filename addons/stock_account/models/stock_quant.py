#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models
fromflectra.tools.float_utilsimportfloat_is_zero


classStockQuant(models.Model):
    _inherit='stock.quant'

    value=fields.Monetary('Value',compute='_compute_value',groups='stock.group_stock_manager')
    currency_id=fields.Many2one('res.currency',compute='_compute_value',groups='stock.group_stock_manager')

    @api.depends('company_id','location_id','owner_id','product_id','quantity')
    def_compute_value(self):
        """ForstandardandAVCOvaluation,computethecurrentaccounting
        valuationofthequantsbymultiplyingthequantityby
        thestandardprice.InsteadforFIFO,usethequantitytimesthe
        averagecost(valuationlayersarenotmanagebylocationsothe
        averagecostisthesameforalllocationandthevaluationfieldis
        aestimationmorethanarealvalue).
        """
        forquantinself:
            quant.currency_id=quant.company_id.currency_id
            #Iftheuserdidn'tenteralocationyetwhileencondingaquant.
            ifnotquant.location_id:
                quant.value=0
                return

            ifnotquant.location_id._should_be_valued()or\
                    (quant.owner_idandquant.owner_id!=quant.company_id.partner_id):
                quant.value=0
                continue
            ifquant.product_id.cost_method=='fifo':
                quantity=quant.product_id.with_company(quant.company_id).quantity_svl
                iffloat_is_zero(quantity,precision_rounding=quant.product_id.uom_id.rounding):
                    quant.value=0.0
                    continue
                average_cost=quant.product_id.with_company(quant.company_id).value_svl/quantity
                quant.value=quant.quantity*average_cost
            else:
                quant.value=quant.quantity*quant.product_id.with_company(quant.company_id).standard_price

    @api.model
    defread_group(self,domain,fields,groupby,offset=0,limit=None,orderby=False,lazy=True):
        """Thisoverrideisdoneinorderforthegroupedlistviewtodisplaythetotalvalueof
        thequantsinsidealocation.Thisdoesn'tworkoutoftheboxbecause`value`isacomputed
        field.
        """
        if'value'notinfields:
            returnsuper(StockQuant,self).read_group(domain,fields,groupby,offset=offset,limit=limit,orderby=orderby,lazy=lazy)
        res=super(StockQuant,self).read_group(domain,fields,groupby,offset=offset,limit=limit,orderby=orderby,lazy=lazy)
        forgroupinres:
            ifgroup.get('__domain'):
                quants=self.search(group['__domain'])
                group['value']=sum(quant.valueforquantinquants)
        returnres
