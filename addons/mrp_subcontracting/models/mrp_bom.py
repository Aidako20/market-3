#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError
fromflectra.osv.expressionimportAND

classMrpBom(models.Model):
    _inherit='mrp.bom'

    type=fields.Selection(selection_add=[
        ('subcontract','Subcontracting')
    ],ondelete={'subcontract':lambdarecs:recs.write({'type':'normal','active':False})})
    subcontractor_ids=fields.Many2many('res.partner','mrp_bom_subcontractor',string='Subcontractors',check_company=True)

    def_bom_subcontract_find(self,product_tmpl=None,product=None,picking_type=None,company_id=False,bom_type='subcontract',subcontractor=False):
        domain=self._bom_find_domain(product_tmpl=product_tmpl,product=product,picking_type=picking_type,company_id=company_id,bom_type=bom_type)
        ifsubcontractor:
            domain=AND([domain,[('subcontractor_ids','parent_of',subcontractor.ids)]])
            returnself.search(domain,order='sequence,product_id',limit=1)
        else:
            returnself.env['mrp.bom']

    @api.constrains('operation_ids','type')
    def_check_subcontracting_no_operation(self):
        ifself.filtered_domain([('type','=','subcontract'),('operation_ids','!=',False)]):
            raiseValidationError(_('YoucannotsetaBillofMaterialwithoperationsassubcontracting.'))
