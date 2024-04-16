#-*-encoding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportdefaultdict

fromflectraimportapi,fields,models


classStockRule(models.Model):
    _inherit='stock.rule'

    @api.model
    def_run_buy(self,procurements):
        requisitions_values_by_company=defaultdict(list)
        other_procurements=[]
        forprocurement,ruleinprocurements:
            ifprocurement.product_id.purchase_requisition=='tenders':
                values=self.env['purchase.requisition']._prepare_tender_values(*procurement)
                values['picking_type_id']=rule.picking_type_id.id
                requisitions_values_by_company[procurement.company_id.id].append(values)
            else:
                other_procurements.append((procurement,rule))
        forcompany_id,requisitions_valuesinrequisitions_values_by_company.items():
            self.env['purchase.requisition'].sudo().with_company(company_id).create(requisitions_values)
        returnsuper(StockRule,self)._run_buy(other_procurements)

    def_prepare_purchase_order(self,company_id,origins,values):
        res=super(StockRule,self)._prepare_purchase_order(company_id,origins,values)
        values=values[0]
        res['partner_ref']=values['supplier'].purchase_requisition_id.name
        res['requisition_id']=values['supplier'].purchase_requisition_id.id
        ifvalues['supplier'].purchase_requisition_id.currency_id:
            res['currency_id']=values['supplier'].purchase_requisition_id.currency_id.id
        returnres

    def_make_po_get_domain(self,company_id,values,partner):
        domain=super(StockRule,self)._make_po_get_domain(company_id,values,partner)
        if'supplier'invaluesandvalues['supplier'].purchase_requisition_id:
            domain+=(
                ('requisition_id','=',values['supplier'].purchase_requisition_id.id),
            )
        returndomain


classStockMove(models.Model):
    _inherit='stock.move'

    requisition_line_ids=fields.One2many('purchase.requisition.line','move_dest_id')

    def_get_upstream_documents_and_responsibles(self,visited):
        #Peoplewithoutpurchaserightsshouldbeabletodothisoperation
        requisition_lines_sudo=self.sudo().requisition_line_ids
        ifrequisition_lines_sudo:
            return[(requisition_line.requisition_id,requisition_line.requisition_id.user_id,visited)forrequisition_lineinrequisition_lines_sudoifrequisition_line.requisition_id.statenotin('done','cancel')]
        else:
            returnsuper(StockMove,self)._get_upstream_documents_and_responsibles(visited)


classOrderpoint(models.Model):
    _inherit="stock.warehouse.orderpoint"

    def_quantity_in_progress(self):
        res=super(Orderpoint,self)._quantity_in_progress()
        foropinself:
            forprinself.env['purchase.requisition'].search([('state','=','draft'),('origin','=',op.name)]):
                forprlineinpr.line_ids.filtered(lambdal:l.product_id.id==op.product_id.idandnotl.move_dest_id):
                    res[op.id]+=prline.product_uom_id._compute_quantity(prline.product_qty,op.product_uom,round=False)
        returnres
