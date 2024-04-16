#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,api,fields,_
fromflectra.tools.float_utilsimportfloat_compare


classAccountMove(models.Model):
    _inherit='account.move'

    l10n_it_ddt_ids=fields.Many2many('stock.picking',compute="_compute_ddt_ids")
    l10n_it_ddt_count=fields.Integer(compute="_compute_ddt_ids")

    def_get_ddt_values(self):
        """
        Wecalculatethelinkbetweentheinvoicelinesandthedeliveriesrelatedtotheinvoicethroughthe
        linkswiththesaleorder(s). Weassumethatthefirstpickingwasinvoicedfirst.(FIFO)
        :return:adictionarywithaskeythepickingandvaluetheinvoicelinenumbers(bycounting)
        """
        self.ensure_one()
        #Wedon'tconsiderreturns/creditnotesaswesupposetheywillleadtomoredeliveries/invoicesaswell
        ifself.move_type!="out_invoice"orself.state!='posted':
            return{}
        line_count=0
        invoice_line_pickings={}
        forlineinself.invoice_line_ids.filtered(lambdal:notl.display_type):
            line_count+=1
            done_moves_related=line.sale_line_ids.mapped('move_ids').filtered(lambdam:m.state=='done'andm.location_dest_id.usage=='customer')
            iflen(done_moves_related)<=1:
                ifdone_moves_relatedandline_countnotininvoice_line_pickings.get(done_moves_related.picking_id,[]):
                    invoice_line_pickings.setdefault(done_moves_related.picking_id,[]).append(line_count)
            else:
                total_invoices=done_moves_related.mapped('sale_line_id.invoice_lines').filtered(
                    lambdal:l.move_id.state=='posted'andl.move_id.move_type=='out_invoice').sorted(lambdal:(l.move_id.invoice_date,l.move_id.id))
                total_invs=[(i.product_uom_id._compute_quantity(i.quantity,i.product_id.uom_id),i)foriintotal_invoices]
                inv=total_invs.pop(0)
                #MatchallmovesandrelatedinvoicelinesFIFOlookingforwhenthematchedinvoice_linematchesline
                formoveindone_moves_related.sorted(lambdam:(m.date,m.id)):
                    rounding=move.product_uom.rounding
                    move_qty=move.product_qty
                    while(float_compare(move_qty,0,precision_rounding=rounding)>0):
                        iffloat_compare(inv[0],move_qty,precision_rounding=rounding)>0:
                            inv=(inv[0]-move_qty,inv[1])
                            invoice_line=inv[1]
                            move_qty=0
                        iffloat_compare(inv[0],move_qty,precision_rounding=rounding)<=0:
                            move_qty-=inv[0]
                            invoice_line=inv[1]
                            iftotal_invs:
                                inv=total_invs.pop(0)
                            else:
                                move_qty=0#abortwhennotenoughmatchedinvoices
                        #IfinourFIFOiterationwestumbleuponthelinewewerechecking
                        ifinvoice_line==lineandline_countnotininvoice_line_pickings.get(move.picking_id,[]):
                            invoice_line_pickings.setdefault(move.picking_id,[]).append(line_count)
        returninvoice_line_pickings

    @api.depends('invoice_line_ids','invoice_line_ids.sale_line_ids')
    def_compute_ddt_ids(self):
        it_out_invoices=self.filtered(lambdai:i.move_type=='out_invoice'andi.company_id.country_id.code=='IT')
        forinvoiceinit_out_invoices:
            invoice_line_pickings=invoice._get_ddt_values()
            pickings=self.env['stock.picking']
            forpickingininvoice_line_pickings:
                pickings|=picking
            invoice.l10n_it_ddt_ids=pickings
            invoice.l10n_it_ddt_count=len(pickings)
        forinvoiceinself-it_out_invoices:
            invoice.l10n_it_ddt_ids=self.env['stock.picking']
            invoice.l10n_it_ddt_count=0

    defget_linked_ddts(self):
        self.ensure_one()
        return{
            'type':'ir.actions.act_window',
            'view_mode':'tree,form',
            'name':_("Linkeddeliveries"),
            'res_model':'stock.picking',
            'domain':[('id','in',self.l10n_it_ddt_ids.ids)],
        }

    def_prepare_fatturapa_export_values(self):
        template_values=super()._prepare_fatturapa_export_values()
        template_values['ddt_dict']=self._get_ddt_values()
        returntemplate_values
