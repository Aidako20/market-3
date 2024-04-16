#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportForm
fromdatetimeimportdatetime,timedelta

fromflectra.fieldsimportDatetimeasDt
fromflectra.exceptionsimportUserError
fromflectra.addons.mrp.tests.commonimportTestMrpCommon


classTestMrpCancelMO(TestMrpCommon):

    deftest_cancel_mo_without_routing_1(self):
        """CancelaManufacturingOrderwithnorouting,noproduction.
        """
        #CreateMO
        manufacturing_order=self.generate_mo()[0]
        #Donothing,cancelit
        manufacturing_order.action_cancel()
        #ChecktheMOanditsmovesarecancelled
        self.assertEqual(manufacturing_order.state,'cancel',"MOshouldbeincancelstate.")
        self.assertEqual(manufacturing_order.move_raw_ids[0].state,'cancel',
            "CancelledMOrawmovesmustbecancelledaswell.")
        self.assertEqual(manufacturing_order.move_raw_ids[1].state,'cancel',
            "CancelledMOrawmovesmustbecancelledaswell.")
        self.assertEqual(manufacturing_order.move_finished_ids.state,'cancel',
            "CancelledMOfinishedmovemustbecancelledaswell.")

    deftest_cancel_mo_without_routing_2(self):
        """CancelaManufacturingOrderwithnoroutingbutsomeproductions.
        """
        #CreateMO
        manufacturing_order=self.generate_mo()[0]
        #Producesomequantity
        mo_form=Form(manufacturing_order)
        mo_form.qty_producing=2
        manufacturing_order=mo_form.save()
        #Cancelit
        manufacturing_order.action_cancel()
        #Checkit'scancelled
        self.assertEqual(manufacturing_order.state,'cancel',"MOshouldbeincancelstate.")
        self.assertEqual(manufacturing_order.move_raw_ids[0].state,'cancel',
            "CancelledMOrawmovesmustbecancelledaswell.")
        self.assertEqual(manufacturing_order.move_raw_ids[1].state,'cancel',
            "CancelledMOrawmovesmustbecancelledaswell.")
        self.assertEqual(manufacturing_order.move_finished_ids.state,'cancel',
            "CancelledMOfinishedmovemustbecancelledaswell.")

    deftest_cancel_mo_without_routing_3(self):
        """CancelaManufacturingOrderwithnoroutingbutsomeproductions
        afterpostinventory.
        """
        #CreateMO
        manufacturing_order=self.generate_mo(consumption='strict')[0]
        #Producesomequantity(notalltoavoidtodonetheMOwhenpostinventory)
        mo_form=Form(manufacturing_order)
        mo_form.qty_producing=2
        manufacturing_order=mo_form.save()
        #PostInventory
        manufacturing_order._post_inventory()
        #CanceltheMO
        manufacturing_order.action_cancel()
        #CheckMOismarkedasdoneanditsSMLaredoneorcancelled
        self.assertEqual(manufacturing_order.state,'done',"MOshouldbeindonestate.")
        self.assertEqual(manufacturing_order.move_raw_ids[0].state,'done',
            "Dueto'post_inventory',somemoverawmuststayindonestate")
        self.assertEqual(manufacturing_order.move_raw_ids[1].state,'done',
            "Dueto'post_inventory',somemoverawmuststayindonestate")
        self.assertEqual(manufacturing_order.move_raw_ids[2].state,'cancel',
            "TheothermoverawarecancelledliketheirMO.")
        self.assertEqual(manufacturing_order.move_raw_ids[3].state,'cancel',
            "TheothermoverawarecancelledliketheirMO.")
        self.assertEqual(manufacturing_order.move_finished_ids[0].state,'done',
            "Dueto'post_inventory',amovefinishedmuststayindonestate")
        self.assertEqual(manufacturing_order.move_finished_ids[1].state,'cancel',
            "TheothermovefinishediscancelledlikeitsMO.")

    deftest_unlink_mo(self):
        """TrytounlinkaManufacturingOrder,andcheckit'spossibleornot
        dependingoftheMOstate(mustbeincancelstatetobeunlinked,but
        theunlinkmethodwilltrytocancelMObeforeunlinkthem).
        """
        #Case#1:CreateMO,donothingandtrytounlinkit(canbedeleted)
        manufacturing_order=self.generate_mo()[0]
        self.assertEqual(manufacturing_order.exists().state,'confirmed')
        manufacturing_order.unlink()
        #ChecktheMOisdeleted.
        self.assertEqual(manufacturing_order.exists().state,False)

        #Case#2:CreateMO,makeandpostsomeproduction,thentrytounlink
        #it(cannotbedeleted)
        manufacturing_order=self.generate_mo()[0]
        #Producesomequantity(notalltoavoidtodonetheMOwhenpostinventory)
        mo_form=Form(manufacturing_order)
        mo_form.qty_producing=2
        manufacturing_order=mo_form.save()
        #PostInventory
        manufacturing_order._post_inventory()
        #UnlinktheMOmustraisesanUserErrorsinceitcannotbereallycancelled
        self.assertEqual(manufacturing_order.exists().state,'progress')
        withself.assertRaises(UserError):
            manufacturing_order.unlink()

    deftest_cancel_mo_with_workorder(self):
        """
            Createamanufacturingorderwithoutcomponentandwithaworkorder
            andcheckthatwhenyoucanceltheMO,theWOisalsocanceled.
        """

        bom=self.env['mrp.bom'].create({
            'product_id':self.product_2.id,
            'product_tmpl_id':self.product_2.product_tmpl_id.id,
            'product_uom_id':self.product_2.uom_id.id,
            'consumption':'flexible',
            'product_qty':1.0,
            'operation_ids':[
                (0,0,{'name':'test_wo','workcenter_id':self.workcenter_1.id,'time_cycle':15,'sequence':1}),
            ],
            'type':'normal',
            'sequence':2,
            'bom_line_ids':[]
            })

        #CreateMO
        production_form=Form(self.env['mrp.production'])
        production_form.product_id=self.product_2
        production_form.bom_id=bom
        manufacturing_order=production_form.save()

        #Checkthatthereisnocomponent
        self.assertFalse(manufacturing_order.move_raw_ids.id)

        #CanceltheMO
        manufacturing_order.action_cancel()

        #CheckthatMOandWOarecanceled
        self.assertEqual(manufacturing_order.state,'cancel',"MOshouldbeincancelstate.")
        self.assertEqual(manufacturing_order.workorder_ids.state,'cancel','MOworkordersmustbecancelledaswell.')
