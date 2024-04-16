#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.tests.commonimportForm
fromflectra.addons.mail.tests.commonimportmail_new_test_user
fromflectra.addons.stock.tests.test_reportimportTestReportsCommon


classTestPurchaseStockReports(TestReportsCommon):
    deftest_report_forecast_1_purchase_order_multi_receipt(self):
        """CreateaPOfor5product,receivethemthenincreasethequantityto10.
        """
        po_form=Form(self.env['purchase.order'])
        po_form.partner_id=self.partner
        withpo_form.order_line.new()asline:
            line.product_id=self.product
            line.product_qty=5
        po=po_form.save()

        #Checksthereport.
        report_values,docs,lines=self.get_report_forecast(product_template_ids=self.product_template.ids)
        draft_picking_qty_in=docs['draft_picking_qty']['in']
        draft_purchase_qty=docs['draft_purchase_qty']
        pending_qty_in=docs['qty']['in']
        self.assertEqual(len(lines),0,"Musthave0linefornow.")
        self.assertEqual(draft_picking_qty_in,0)
        self.assertEqual(draft_purchase_qty,5)
        self.assertEqual(pending_qty_in,5)

        #ConfirmsthePOandchecksthereportagain.
        po.button_confirm()
        report_values,docs,lines=self.get_report_forecast(product_template_ids=self.product_template.ids)
        draft_picking_qty_in=docs['draft_picking_qty']['in']
        draft_purchase_qty=docs['draft_purchase_qty']
        pending_qty_in=docs['qty']['in']
        self.assertEqual(len(lines),1)
        self.assertEqual(lines[0]['document_in'].id,po.id)
        self.assertEqual(lines[0]['quantity'],5)
        self.assertEqual(lines[0]['document_out'],False)
        self.assertEqual(draft_picking_qty_in,0)
        self.assertEqual(draft_purchase_qty,0)
        self.assertEqual(pending_qty_in,0)

        #Receives5products.
        receipt=po.picking_ids
        res_dict=receipt.button_validate()
        wizard=Form(self.env[res_dict['res_model']].with_context(res_dict['context'])).save()
        wizard.process()
        report_values,docs,lines=self.get_report_forecast(product_template_ids=self.product_template.ids)
        draft_picking_qty_in=docs['draft_picking_qty']['in']
        draft_purchase_qty=docs['draft_purchase_qty']
        pending_qty_in=docs['qty']['in']
        self.assertEqual(len(lines),0)
        self.assertEqual(draft_picking_qty_in,0)
        self.assertEqual(draft_purchase_qty,0)
        self.assertEqual(pending_qty_in,0)

        #IncreasethePOquantityto10,somustcreateasecondreceipt.
        po_form=Form(po)
        withpo_form.order_line.edit(0)asline:
            line.product_qty=10
        po=po_form.save()
        #Checksthereport.
        report_values,docs,lines=self.get_report_forecast(product_template_ids=self.product_template.ids)
        draft_picking_qty_in=docs['draft_picking_qty']['in']
        draft_purchase_qty=docs['draft_purchase_qty']
        pending_qty_in=docs['qty']['in']
        self.assertEqual(len(lines),1,"Musthave1linefornow.")
        self.assertEqual(lines[0]['document_in'].id,po.id)
        self.assertEqual(lines[0]['quantity'],5)
        self.assertEqual(draft_picking_qty_in,0)
        self.assertEqual(draft_purchase_qty,0)
        self.assertEqual(pending_qty_in,0)

    deftest_report_forecast_2_purchase_order_three_step_receipt(self):
        """CreateaPOfor4product,receivethemthenincreasethequantity
        to10,butusethreestepsreceipt.
        """
        grp_multi_loc=self.env.ref('stock.group_stock_multi_locations')
        grp_multi_routes=self.env.ref('stock.group_adv_location')
        self.env.user.write({'groups_id':[(4,grp_multi_loc.id)]})
        self.env.user.write({'groups_id':[(4,grp_multi_routes.id)]})
        #Configurewarehouse.
        warehouse=self.env.ref('stock.warehouse0')
        warehouse.reception_steps='three_steps'

        po_form=Form(self.env['purchase.order'])
        po_form.partner_id=self.partner
        withpo_form.order_line.new()asline:
            line.product_id=self.product
            line.product_qty=4
        po=po_form.save()

        #Checksthereport->Mustbeemptyfornow,justdisplaysomependingqty.
        report_values,docs,lines=self.get_report_forecast(product_template_ids=self.product_template.ids)
        draft_picking_qty_in=docs['draft_picking_qty']['in']
        draft_purchase_qty=docs['draft_purchase_qty']
        pending_qty_in=docs['qty']['in']
        self.assertEqual(len(lines),0,"Musthave0linefornow.")
        self.assertEqual(draft_picking_qty_in,0)
        self.assertEqual(draft_purchase_qty,4)
        self.assertEqual(pending_qty_in,4)

        #ConfirmsthePOandchecksthereportagain.
        po.button_confirm()
        report_values,docs,lines=self.get_report_forecast(product_template_ids=self.product_template.ids)
        draft_picking_qty_in=docs['draft_picking_qty']['in']
        draft_purchase_qty=docs['draft_purchase_qty']
        pending_qty_in=docs['qty']['in']
        self.assertEqual(len(lines),1)
        self.assertEqual(lines[0]['document_in'].id,po.id)
        self.assertEqual(lines[0]['quantity'],4)
        self.assertEqual(lines[0]['document_out'],False)
        self.assertEqual(draft_picking_qty_in,0)
        self.assertEqual(draft_purchase_qty,0)
        self.assertEqual(pending_qty_in,0)
        #Getbackthedifferenttransfers.
        receipt=po.picking_ids

        #Receives4products.
        res_dict=receipt.button_validate()
        wizard=Form(self.env[res_dict['res_model']].with_context(res_dict['context'])).save()
        wizard.process()
        report_values,docs,lines=self.get_report_forecast(product_template_ids=self.product_template.ids)
        draft_picking_qty_in=docs['draft_picking_qty']['in']
        draft_purchase_qty=docs['draft_purchase_qty']
        pending_qty_in=docs['qty']['in']
        self.assertEqual(len(lines),0)
        self.assertEqual(draft_picking_qty_in,0)
        self.assertEqual(draft_purchase_qty,0)
        self.assertEqual(pending_qty_in,0)

        #IncreasethePOquantityto10,somustcreateasecondreceipt.
        po_form=Form(po)
        withpo_form.order_line.edit(0)asline:
            line.product_qty=10
        po=po_form.save()
        #Checksthereport.
        report_values,docs,lines=self.get_report_forecast(product_template_ids=self.product_template.ids)
        draft_picking_qty_in=docs['draft_picking_qty']['in']
        draft_purchase_qty=docs['draft_purchase_qty']
        pending_qty_in=docs['qty']['in']
        self.assertEqual(len(lines),1)
        self.assertEqual(lines[0]['document_in'].id,po.id)
        self.assertEqual(lines[0]['quantity'],6)
        self.assertEqual(draft_picking_qty_in,0)
        self.assertEqual(draft_purchase_qty,0)
        self.assertEqual(pending_qty_in,0)

    deftest_approval_and_forecasted_qty(self):
        """
        WhenaPOiswaitingforanapproval,itsquantitiesshouldbeincluded
        inthedraftquantitycount
        """
        self.env.company.po_double_validation='two_step'
        self.env.company.po_double_validation_amount=0

        basic_purchase_user=mail_new_test_user(
            self.env,
            login='basic_purchase_user',
            groups='base.group_user,purchase.group_purchase_user',
        )

        po_form=Form(self.env['purchase.order'])
        po_form.partner_id=self.partner
        withpo_form.order_line.new()asline:
            line.product_id=self.product
            line.product_qty=50
        po_form.save()

        po_form=Form(self.env['purchase.order'])
        po_form.partner_id=self.partner
        withpo_form.order_line.new()asline:
            line.product_id=self.product
            line.product_qty=100
        po=po_form.save()
        po.with_user(basic_purchase_user).button_confirm()

        docs=self.get_report_forecast(product_template_ids=self.product_template.ids)[1]
        self.assertEqual(docs['draft_purchase_qty'],150)

    deftest_vendor_delay_report_with_uom(self):
        """
        PO12unitsxP
        Receive1dozenxP
        ->100%received
        """
        uom_12=self.env.ref('uom.product_uom_dozen')

        po_form=Form(self.env['purchase.order'])
        po_form.partner_id=self.partner
        withpo_form.order_line.new()asline:
            line.product_id=self.product
            line.product_qty=12
        po=po_form.save()
        po.button_confirm()

        receipt=po.picking_ids
        receipt_move=receipt.move_lines
        receipt_move.move_line_ids.unlink()
        receipt_move.move_line_ids=[(0,0,{
            'location_id':receipt_move.location_id.id,
            'location_dest_id':receipt_move.location_dest_id.id,
            'product_id':self.product.id,
            'product_uom_id':uom_12.id,
            'qty_done':1,
            'picking_id':receipt.id,
        })]
        receipt.button_validate()

        data=self.env['vendor.delay.report'].read_group(
            [('partner_id','=',self.partner.id)],
            ['product_id','on_time_rate','qty_on_time','qty_total'],
            ['product_id'],
        )[0]
        self.assertEqual(data['qty_on_time'],12)
        self.assertEqual(data['qty_total'],12)
        self.assertEqual(data['on_time_rate'],100)

    deftest_vendor_delay_report_with_multi_location(self):
        """
        PO10unitsxP
        Receive
            -6xPinChildLocation01
            -4xPinChildLocation02
        ->100%received
        """
        child_loc_01,child_loc_02=self.stock_location.child_ids

        po_form=Form(self.env['purchase.order'])
        po_form.partner_id=self.partner
        withpo_form.order_line.new()asline:
            line.product_id=self.product
            line.product_qty=10
        po=po_form.save()
        po.button_confirm()

        receipt=po.picking_ids
        receipt_move=receipt.move_lines
        receipt_move.move_line_ids.unlink()
        receipt_move.move_line_ids=[(0,0,{
            'location_id':receipt_move.location_id.id,
            'location_dest_id':child_loc_01.id,
            'product_id':self.product.id,
            'product_uom_id':self.product.uom_id.id,
            'qty_done':6,
            'picking_id':receipt.id,
        }),(0,0,{
            'location_id':receipt_move.location_id.id,
            'location_dest_id':child_loc_02.id,
            'product_id':self.product.id,
            'product_uom_id':self.product.uom_id.id,
            'qty_done':4,
            'picking_id':receipt.id,
        })]
        receipt.button_validate()

        data=self.env['vendor.delay.report'].read_group(
            [('partner_id','=',self.partner.id)],
            ['product_id','on_time_rate','qty_on_time','qty_total'],
            ['product_id'],
        )[0]
        self.assertEqual(data['qty_on_time'],10)
        self.assertEqual(data['qty_total'],10)
        self.assertEqual(data['on_time_rate'],100)

    deftest_vendor_delay_report_with_backorder(self):
        """
        PO10unitsxP
        Receive6xPwithbackorder
        ->60%received
        Processthebackorder
        ->100%received
        """
        po_form=Form(self.env['purchase.order'])
        po_form.partner_id=self.partner
        withpo_form.order_line.new()asline:
            line.product_id=self.product
            line.product_qty=10
        po=po_form.save()
        po.button_confirm()

        receipt01=po.picking_ids
        receipt01_move=receipt01.move_lines
        receipt01_move.quantity_done=6
        action=receipt01.button_validate()
        Form(self.env[action['res_model']].with_context(action['context'])).save().process()

        data=self.env['vendor.delay.report'].read_group(
            [('partner_id','=',self.partner.id)],
            ['product_id','on_time_rate','qty_on_time','qty_total'],
            ['product_id'],
        )[0]
        self.assertEqual(data['qty_on_time'],6)
        self.assertEqual(data['qty_total'],10)
        self.assertEqual(data['on_time_rate'],60)

        receipt02=receipt01.backorder_ids
        receipt02.move_lines.quantity_done=4
        receipt02.button_validate()

        data=self.env['vendor.delay.report'].read_group(
            [('partner_id','=',self.partner.id)],
            ['product_id','on_time_rate','qty_on_time','qty_total'],
            ['product_id'],
        )[0]
        self.assertEqual(data['qty_on_time'],10)
        self.assertEqual(data['qty_total'],10)
        self.assertEqual(data['on_time_rate'],100)

    deftest_vendor_delay_report_without_backorder(self):
        """
        PO10unitsxP
        Receive6xPwithoutbackorder
        ->60%received
        """
        po_form=Form(self.env['purchase.order'])
        po_form.partner_id=self.partner
        withpo_form.order_line.new()asline:
            line.product_id=self.product
            line.product_qty=10
        po=po_form.save()
        po.button_confirm()

        receipt01=po.picking_ids
        receipt01_move=receipt01.move_lines
        receipt01_move.quantity_done=6
        action=receipt01.button_validate()
        Form(self.env[action['res_model']].with_context(action['context'])).save().process_cancel_backorder()

        data=self.env['vendor.delay.report'].read_group(
            [('partner_id','=',self.partner.id)],
            ['product_id','on_time_rate','qty_on_time','qty_total'],
            ['product_id'],
        )[0]
        self.assertEqual(data['qty_on_time'],6)
        self.assertEqual(data['qty_total'],10)
        self.assertEqual(data['on_time_rate'],60)
