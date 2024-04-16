#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResPartner(models.Model):
    _inherit='res.partner'

    property_stock_subcontractor=fields.Many2one(
        'stock.location',string="SubcontractorLocation",company_dependent=True,
        help="Thestocklocationusedassourceanddestinationwhensending\
        goodstothiscontactduringasubcontractingprocess.")
    is_subcontractor=fields.Boolean(
        string="Subcontractor",store=False,search="_search_is_subcontractor")

    def_search_is_subcontractor(self,operator,value):
        assertoperatorin('=','!=','<>')andvaluein(True,False),'Operationnotsupported'
        subcontractor_ids=self.env['mrp.bom'].search(
            [('type','=','subcontract')]).subcontractor_ids.ids
        if(operator=='='andvalueisTrue)or(operatorin('<>','!=')andvalueisFalse):
            search_operator='in'
        else:
            search_operator='notin'
        return[('id',search_operator,subcontractor_ids)]
