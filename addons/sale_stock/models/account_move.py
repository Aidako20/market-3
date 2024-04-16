#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportdefaultdict

fromflectraimportfields,models
fromflectra.toolsimportfloat_is_zero,float_compare
fromflectra.tools.miscimportformatLang


classAccountMove(models.Model):
    _inherit='account.move'

    def_stock_account_get_last_step_stock_moves(self):
        """Overriddenfromstock_account.
        Returnsthestockmovesassociatedtothisinvoice."""
        rslt=super(AccountMove,self)._stock_account_get_last_step_stock_moves()
        forinvoiceinself.filtered(lambdax:x.move_type=='out_invoice'):
            rslt+=invoice.mapped('invoice_line_ids.sale_line_ids.move_ids').filtered(lambdax:x.state=='done'andx.location_dest_id.usage=='customer')
        forinvoiceinself.filtered(lambdax:x.move_type=='out_refund'):
            rslt+=invoice.mapped('reversed_entry_id.invoice_line_ids.sale_line_ids.move_ids').filtered(lambdax:x.state=='done'andx.location_id.usage=='customer')
            #AddrefundsgeneratedfromtheSO
            rslt+=invoice.mapped('invoice_line_ids.sale_line_ids.move_ids').filtered(lambdax:x.state=='done'andx.location_id.usage=='customer')
        returnrslt

    def_get_invoiced_lot_values(self):
        """Getandpreparedatatoshowatableofinvoicedlotontheinvoice'sreport."""
        self.ensure_one()
        ifself.state=='draft'ornotself.invoice_dateorself.move_typenotin('out_invoice','out_refund'):
            return[]

        current_invoice_amls=self.invoice_line_ids.filtered(lambdaaml:notaml.display_typeandaml.product_idandaml.product_id.typein('consu','product')andaml.quantity)
        all_invoices_amls=current_invoice_amls.sale_line_ids.invoice_lines.filtered(lambdaaml:aml.move_id.state=='posted').sorted(lambdaaml:(aml.date,aml.move_name,aml.id))
        index=all_invoices_amls.ids.index(current_invoice_amls[:1].id)ifcurrent_invoice_amls[:1]inall_invoices_amlselse0
        previous_amls=all_invoices_amls[:index]
        invoiced_qties=current_invoice_amls._get_invoiced_qty_per_product()
        invoiced_products=invoiced_qties.keys()

        ifself.move_type=='out_invoice':
            #filterouttheinvoicesthathavebeenfullyrefundandre-invoiceotherwise,thequantitieswouldbe
            #consumedbythereversedinvoiceandwon'tbeprintonthenewdraftinvoice
            previous_amls=previous_amls.filtered(lambdaaml:aml.move_id.payment_state!='reversed')

        previous_qties_invoiced=previous_amls._get_invoiced_qty_per_product()

        ifself.move_type=='out_refund':
            #weswapthesignbecauseit'sarefund,anditwouldprintnegativenumberotherwise
            forpinprevious_qties_invoiced:
                previous_qties_invoiced[p]=-previous_qties_invoiced[p]
            forpininvoiced_qties:
                invoiced_qties[p]=-invoiced_qties[p]

        qties_per_lot=defaultdict(float)
        previous_qties_delivered=defaultdict(float)
        stock_move_lines=current_invoice_amls.sale_line_ids.move_ids.move_line_ids.filtered(lambdasml:sml.state=='done'andsml.lot_id).sorted(lambdasml:(sml.date,sml.id))
        forsmlinstock_move_lines:
            ifsml.product_idnotininvoiced_productsor'customer'notin{sml.location_id.usage,sml.location_dest_id.usage}:
                continue
            product=sml.product_id
            product_uom=product.uom_id
            qty_done=sml.product_uom_id._compute_quantity(sml.qty_done,product_uom)

            #isitastockreturnconsideringthedocumenttype(shoulditbeitthoughtofaspositivelyornegatively?)
            is_stock_return=(
                    self.move_type=='out_invoice'and(sml.location_id.usage,sml.location_dest_id.usage)==('customer','internal')
                    or
                    self.move_type=='out_refund'and(sml.location_id.usage,sml.location_dest_id.usage)==('internal','customer')
            )
            ifis_stock_return:
                returned_qty=min(qties_per_lot[sml.lot_id],qty_done)
                qties_per_lot[sml.lot_id]-=returned_qty
                qty_done=returned_qty-qty_done

            previous_qty_invoiced=previous_qties_invoiced[product]
            previous_qty_delivered=previous_qties_delivered[product]
            #Ifwereturnmorethancurrentlydelivered(i.e.,qty_done<0),weremovethesurplus
            #fromthepreviouslydelivered(andqty_donebecomeszero).Ifit'sadelivery,wefirst
            #trytoreachtheprevious_qty_invoiced
            iffloat_compare(qty_done,0,precision_rounding=product_uom.rounding)<0or\
                    float_compare(previous_qty_delivered,previous_qty_invoiced,precision_rounding=product_uom.rounding)<0:
                previously_done=qty_doneifis_stock_returnelsemin(previous_qty_invoiced-previous_qty_delivered,qty_done)
                previous_qties_delivered[product]+=previously_done
                qty_done-=previously_done

            qties_per_lot[sml.lot_id]+=qty_done

        lot_values=[]
        forlot,qtyinqties_per_lot.items():
            lot_sudo=lot.sudo()
            iffloat_is_zero(invoiced_qties[lot_sudo.product_id],precision_rounding=lot_sudo.product_uom_id.rounding)\
                    orfloat_compare(qty,0,precision_rounding=lot_sudo.product_uom_id.rounding)<=0:
                continue
            invoiced_lot_qty=min(qty,invoiced_qties[lot_sudo.product_id])
            invoiced_qties[lot_sudo.product_id]-=invoiced_lot_qty
            lot_values.append({
                'product_name':lot_sudo.product_id.display_name,
                'quantity':formatLang(self.env,invoiced_lot_qty,dp='ProductUnitofMeasure'),
                'uom_name':lot_sudo.product_uom_id.name,
                'lot_name':lot_sudo.name,
                #Thelotidisneededbylocalizationstoinheritthemethodandaddcustomfieldsontheinvoice'sreport.
                'lot_id':lot_sudo.id,
            })

        returnlot_values


classAccountMoveLine(models.Model):
    _inherit="account.move.line"

    def_sale_can_be_reinvoice(self):
        self.ensure_one()
        returnnotself.is_anglo_saxon_lineandsuper(AccountMoveLine,self)._sale_can_be_reinvoice()

    def_stock_account_get_anglo_saxon_price_unit(self):
        self.ensure_one()
        price_unit=super(AccountMoveLine,self)._stock_account_get_anglo_saxon_price_unit()

        so_line=self.sale_line_idsandself.sale_line_ids[-1]orFalse
        ifso_line:
            is_line_reversing=self.move_id.move_type=='out_refund'
            qty_to_invoice=self.product_uom_id._compute_quantity(self.quantity,self.product_id.uom_id)
            account_moves=so_line.invoice_lines.move_id.filtered(lambdam:m.state=='posted'andbool(m.reversed_entry_id)==is_line_reversing)

            posted_cogs=account_moves.line_ids.filtered(lambdal:l.is_anglo_saxon_lineandl.product_id==self.product_idandl.balance>0)
            qty_invoiced=sum([line.product_uom_id._compute_quantity(line.quantity,line.product_id.uom_id)forlineinposted_cogs])
            value_invoiced=sum(posted_cogs.mapped('balance'))

            reversal_cogs=posted_cogs.move_id.reversal_move_id.line_ids.filtered(lambdal:l.is_anglo_saxon_lineandl.product_id==self.product_idandl.balance>0)
            qty_invoiced-=sum([line.product_uom_id._compute_quantity(line.quantity,line.product_id.uom_id)forlineinreversal_cogs])
            value_invoiced-=sum(reversal_cogs.mapped('balance'))

            product=self.product_id.with_company(self.company_id).with_context(is_returned=is_line_reversing,value_invoiced=value_invoiced)
            average_price_unit=product._compute_average_price(qty_invoiced,qty_to_invoice,so_line.move_ids)
            price_unit=self.product_id.uom_id.with_company(self.company_id)._compute_price(average_price_unit,self.product_uom_id)
        returnprice_unit
