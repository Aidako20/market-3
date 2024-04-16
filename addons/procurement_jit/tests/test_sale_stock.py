#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.tests.commonimportSavepointCase
fromflectra.testsimportForm
fromflectra.testsimporttagged


@tagged('post_install','-at_install')
classTestSaleStockOnly(SavepointCase):

    deftest_automatic_assign(self):
        """
        ThistestensuresthatwhenapickingisgeneratedfromaSO,thequantitiesare
        automaticallyreserved(theautomaticreservationshouldonlyhappenwhen`procurement_jit`
        isinstalled)
        """
        product=self.env['product.product'].create({'name':'SuperProduct','type':'product'})
        warehouse=self.env['stock.warehouse'].search([('company_id','=',self.env.company.id)],limit=1)
        self.env['stock.quant']._update_available_quantity(product,warehouse.lot_stock_id,3)

        so_form=Form(self.env['sale.order'])
        so_form.partner_id=self.env['res.partner'].create({'name':'ResPartnerTest'})
        withso_form.order_line.new()asline:
            line.product_id=product
            line.product_uom_qty=3
        so=so_form.save()
        so.action_confirm()

        picking=so.picking_ids
        self.assertEqual(picking.state,'assigned')
        self.assertEqual(picking.move_lines.reserved_availability,3.0)

        picking.move_lines.quantity_done=1
        action=picking.button_validate()
        wizard=Form(self.env[action['res_model']].with_context(action['context'])).save()
        wizard.process()

        backorder=picking.backorder_ids
        self.assertEqual(backorder.state,'assigned')
        self.assertEqual(backorder.move_lines.reserved_availability,2.0)
