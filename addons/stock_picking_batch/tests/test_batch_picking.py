#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime,timedelta

fromflectra.testsimportForm,tagged
fromflectra.tests.commonimportTransactionCase


classTestBatchPicking(TransactionCase):

    defsetUp(self):
        """Createapickingbatchwithtwopickingsfromstocktocustomer"""
        super(TestBatchPicking,self).setUp()
        self.stock_location=self.env.ref('stock.stock_location_stock')
        self.customer_location=self.env.ref('stock.stock_location_customers')
        self.picking_type_out=self.env['ir.model.data'].xmlid_to_res_id('stock.picking_type_out')
        self.productA=self.env['product.product'].create({
            'name':'ProductA',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
        })
        self.productB=self.env['product.product'].create({
            'name':'ProductB',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
        })

        self.picking_client_1=self.env['stock.picking'].create({
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'picking_type_id':self.picking_type_out,
            'company_id':self.env.company.id,
        })

        self.env['stock.move'].create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':10,
            'product_uom':self.productA.uom_id.id,
            'picking_id':self.picking_client_1.id,
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
        })

        self.picking_client_2=self.env['stock.picking'].create({
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'picking_type_id':self.picking_type_out,
            'company_id':self.env.company.id,
        })

        self.env['stock.move'].create({
            'name':self.productB.name,
            'product_id':self.productB.id,
            'product_uom_qty':10,
            'product_uom':self.productA.uom_id.id,
            'picking_id':self.picking_client_2.id,
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
        })

        self.picking_client_3=self.env['stock.picking'].create({
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
            'picking_type_id':self.picking_type_out,
            'company_id':self.env.company.id,
        })

        self.env['stock.move'].create({
            'name':self.productB.name,
            'product_id':self.productB.id,
            'product_uom_qty':10,
            'product_uom':self.productA.uom_id.id,
            'picking_id':self.picking_client_3.id,
            'location_id':self.stock_location.id,
            'location_dest_id':self.customer_location.id,
        })

        self.batch=self.env['stock.picking.batch'].create({
            'name':'Batch1',
            'company_id':self.env.company.id,
            'picking_ids':[(4,self.picking_client_1.id),(4,self.picking_client_2.id)]
        })

    deftest_batch_scheduled_date(self):
        """Testtomakesurethecorrectscheduleddateissetforbothabatchanditspickings.
        Settingabatch'sscheduleddatemanuallyhasdifferentbehaviorfromwhenitisautomatically
        set/updatedviacompute.
        """

        now=datetime.now().replace(microsecond=0)
        self.batch.scheduled_date=now

        #TODO:thistestcannotcurrentlyhandletheonchangescheduled_datelogicbecauseoftestform
        #viewnothandlingtheM2Mwidgetassignedtopicking_ids(O2M).Hopefullyifthischangesthen
        #commentedpartsofthistestcanbeusedlater.


        #manuallysetbatchscheduleddate=>picking'sscheduleddatesautoupdatetomatch(onchangelogictest)
        #withForm(self.batch)asbatch_form:
            #batch_form.scheduled_date=now-timedelta(days=1)
            #batch_form.save()
        #self.assertEqual(self.batch.scheduled_date,self.picking_client_1.scheduled_date)
        #self.assertEqual(self.batch.scheduled_date,self.picking_client_2.scheduled_date)

        picking1_scheduled_date=now-timedelta(days=2)
        picking2_scheduled_date=now-timedelta(days=3)
        picking3_scheduled_date=now-timedelta(days=4)

        #manuallyupdatepickingscheduleddates=>batch'sscheduleddateautoupdatetomatchlowestvalue
        self.picking_client_1.scheduled_date=picking1_scheduled_date
        self.picking_client_2.scheduled_date=picking2_scheduled_date
        self.assertEqual(self.batch.scheduled_date,self.picking_client_2.scheduled_date)
        #butindividualpickingskeeporiginalscheduleddates
        self.assertEqual(self.picking_client_1.scheduled_date,picking1_scheduled_date)
        self.assertEqual(self.picking_client_2.scheduled_date,picking2_scheduled_date)

        #addanewpickingwithanearlierscheduleddate=>batch'sscheduleddateshouldauto-update
        self.picking_client_3.scheduled_date=picking3_scheduled_date
        self.batch.write({'picking_ids':[(4,self.picking_client_3.id)]})
        self.assertEqual(self.batch.scheduled_date,self.picking_client_3.scheduled_date)

        #removethatpickingandbatchscheduleddateshouldauto-updatetonextmindate
        self.batch.write({'picking_ids':[(3,self.picking_client_3.id)]})
        self.assertEqual(self.batch.scheduled_date,self.picking_client_2.scheduled_date)

        #directlyaddnewpickingwithanearlierscheduleddate=>batch'sscheduleddateautoupdatestomatch,
        #butexistingpickingsdonot(onchangelogictest)
        #withForm(self.batch)asbatch_form:
        #    batch_form.picking_ids.add(self.picking_client_3)
        #    batch_form.save()
        ##individualpickingskeeporiginalscheduleddates
        self.assertEqual(self.picking_client_1.scheduled_date,picking1_scheduled_date)
        self.assertEqual(self.picking_client_2.scheduled_date,picking2_scheduled_date)
        #self.assertEqual(self.batch.scheduled_date,self.picking_client_3.scheduled_date)
        #self.batch.write({'picking_ids':[(3,self.picking_client_3.id)]})


        #removeallpickingsandbatchscheduleddateshoulddefaulttonone
        self.batch.write({'picking_ids':[(3,self.picking_client_1.id)]})
        self.batch.write({'picking_ids':[(3,self.picking_client_2.id)]})
        self.assertEqual(self.batch.scheduled_date,False)

    deftest_simple_batch_with_manual_qty_done(self):
        """Testasimplebatchpickingwithallquantityforpickingavailable.
        Theusersetallthequantity_doneonpickingmanuallyandnowizardareused.
        """
        self.env['stock.quant']._update_available_quantity(self.productA,self.stock_location,10.0)
        self.env['stock.quant']._update_available_quantity(self.productB,self.stock_location,10.0)

        #Confirmbatch,pickingsshouldnotbeautomaticallyassigned.
        self.batch.action_confirm()
        self.assertEqual(self.picking_client_1.state,'confirmed','Picking1shouldbeconfirmed')
        self.assertEqual(self.picking_client_2.state,'confirmed','Picking2shouldbeconfirmed')
        #Asktoassign,sopickingsshouldbeassignednow.
        self.batch.action_assign()
        self.assertEqual(self.picking_client_1.state,'assigned','Picking1shouldbeready')
        self.assertEqual(self.picking_client_2.state,'assigned','Picking2shouldbeready')

        self.picking_client_1.move_lines.quantity_done=10
        self.picking_client_2.move_lines.quantity_done=10
        self.batch.action_done()

        self.assertEqual(self.picking_client_1.state,'done','Picking1shouldbedone')
        self.assertEqual(self.picking_client_2.state,'done','Picking2shouldbedone')

        quant_A=self.env['stock.quant']._gather(self.productA,self.stock_location)
        quant_B=self.env['stock.quant']._gather(self.productB,self.stock_location)

        #ensurethatquantityforpickinghasbeenmoved
        self.assertFalse(sum(quant_A.mapped('quantity')))
        self.assertFalse(sum(quant_B.mapped('quantity')))

    deftest_simple_batch_with_wizard(self):
        """Testasimplebatchpickingwithallquantityforpickingavailable.
        Theuserusethewizardinordertocompleteautomaticallythequantity_doneto
        theinitialdemand(orreservedquantityinthistest).
        """
        self.env['stock.quant']._update_available_quantity(self.productA,self.stock_location,10.0)
        self.env['stock.quant']._update_available_quantity(self.productB,self.stock_location,10.0)

        #Confirmbatch,pickingsshouldnotbeautomaticallyassigned.
        self.batch.action_confirm()
        self.assertEqual(self.picking_client_1.state,'confirmed','Picking1shouldbeconfirmed')
        self.assertEqual(self.picking_client_2.state,'confirmed','Picking2shouldbeconfirmed')
        #Asktoassign,sopickingsshouldbeassignednow.
        self.batch.action_assign()
        self.assertEqual(self.picking_client_1.state,'assigned','Picking1shouldbeready')
        self.assertEqual(self.picking_client_2.state,'assigned','Picking2shouldbeready')

        #Thereshouldbeawizardaskingtoprocesspickingwithoutquantitydone
        immediate_transfer_wizard_dict=self.batch.action_done()
        self.assertTrue(immediate_transfer_wizard_dict)
        immediate_transfer_wizard=Form(self.env[(immediate_transfer_wizard_dict.get('res_model'))].with_context(immediate_transfer_wizard_dict['context'])).save()
        self.assertEqual(len(immediate_transfer_wizard.pick_ids),2)
        immediate_transfer_wizard.process()

        self.assertEqual(self.picking_client_1.state,'done','Picking1shouldbedone')
        self.assertEqual(self.picking_client_2.state,'done','Picking2shouldbedone')

        quant_A=self.env['stock.quant']._gather(self.productA,self.stock_location)
        quant_B=self.env['stock.quant']._gather(self.productB,self.stock_location)

        #ensurethatquantityforpickinghasbeenmoved
        self.assertFalse(sum(quant_A.mapped('quantity')))
        self.assertFalse(sum(quant_B.mapped('quantity')))

    deftest_batch_with_backorder_wizard(self):
        """Testasimplebatchpickingwithonlyonequantityfullyavailable.
        Theuserwillsetbyhimselfthequantityreservedforeachpickingand
        runthepickingbatch.Thereshouldbeawizardaskingforabackorder.
        """
        self.env['stock.quant']._update_available_quantity(self.productA,self.stock_location,5.0)
        self.env['stock.quant']._update_available_quantity(self.productB,self.stock_location,10.0)

        #Confirmbatch,pickingsshouldnotbeautomaticallyassigned.
        self.batch.action_confirm()
        self.assertEqual(self.picking_client_1.state,'confirmed','Picking1shouldbeconfirmed')
        self.assertEqual(self.picking_client_2.state,'confirmed','Picking2shouldbeconfirmed')
        #Asktoassign,sopickingsshouldbeassignednow.
        self.batch.action_assign()
        self.assertEqual(self.picking_client_1.state,'assigned','Picking1shouldbeready')
        self.assertEqual(self.picking_client_2.state,'assigned','Picking2shouldbeready')

        self.picking_client_1.move_lines.quantity_done=5
        self.picking_client_2.move_lines.quantity_done=10

        #Thereshouldbeawizardaskingtoprocesspickingwithoutquantitydone
        back_order_wizard_dict=self.batch.action_done()
        self.assertTrue(back_order_wizard_dict)
        back_order_wizard=Form(self.env[(back_order_wizard_dict.get('res_model'))].with_context(back_order_wizard_dict['context'])).save()
        self.assertEqual(len(back_order_wizard.pick_ids),1)
        back_order_wizard.process()

        self.assertEqual(self.picking_client_2.state,'done','Picking2shouldbedone')
        self.assertEqual(self.picking_client_1.state,'done','Picking1shouldbedone')
        self.assertEqual(self.picking_client_1.move_lines.product_uom_qty,5,'initialdemandshouldbe5afterpickingsplit')
        self.assertTrue(self.env['stock.picking'].search([('backorder_id','=',self.picking_client_1.id)]),'nobackordercreated')

        quant_A=self.env['stock.quant']._gather(self.productA,self.stock_location)
        quant_B=self.env['stock.quant']._gather(self.productB,self.stock_location)

        #ensurethatquantityforpickinghasbeenmoved
        self.assertFalse(sum(quant_A.mapped('quantity')))
        self.assertFalse(sum(quant_B.mapped('quantity')))

    deftest_batch_with_immediate_transfer_and_backorder_wizard(self):
        """Testasimplebatchpickingwithonlyoneproductfullyavailable.
        Everythingshouldbeautomatically.Firstonebackorderinordertosetquantity_done
        toreservedquantity.Afterasecondwizardaskingforabackorderforthequantitythat
        hasnotbeenfullytransfered.
        """
        self.env['stock.quant']._update_available_quantity(self.productA,self.stock_location,5.0)
        self.env['stock.quant']._update_available_quantity(self.productB,self.stock_location,10.0)

        #Confirmbatch,pickingsshouldnotbeautomaticallyassigned.
        self.batch.action_confirm()
        self.assertEqual(self.picking_client_1.state,'confirmed','Picking1shouldbeconfirmed')
        self.assertEqual(self.picking_client_2.state,'confirmed','Picking2shouldbeconfirmed')
        #Asktoassign,sopickingsshouldbeassignednow.
        self.batch.action_assign()
        self.assertEqual(self.picking_client_1.state,'assigned','Picking1shouldbeready')
        self.assertEqual(self.picking_client_2.state,'assigned','Picking2shouldbeready')

        #Thereshouldbeawizardaskingtoprocesspickingwithoutquantitydone
        immediate_transfer_wizard_dict=self.batch.action_done()
        self.assertTrue(immediate_transfer_wizard_dict)
        immediate_transfer_wizard=Form(self.env[(immediate_transfer_wizard_dict.get('res_model'))].with_context(immediate_transfer_wizard_dict['context'])).save()
        self.assertEqual(len(immediate_transfer_wizard.pick_ids),2)
        back_order_wizard_dict=immediate_transfer_wizard.process()
        self.assertTrue(back_order_wizard_dict)
        back_order_wizard=Form(self.env[(back_order_wizard_dict.get('res_model'))].with_context(back_order_wizard_dict['context'])).save()
        self.assertEqual(len(back_order_wizard.pick_ids),1)
        back_order_wizard.process()

        self.assertEqual(self.picking_client_1.state,'done','Picking1shouldbedone')
        self.assertEqual(self.picking_client_1.move_lines.product_uom_qty,5,'initialdemandshouldbe5afterpickingsplit')
        self.assertTrue(self.env['stock.picking'].search([('backorder_id','=',self.picking_client_1.id)]),'nobackordercreated')

        quant_A=self.env['stock.quant']._gather(self.productA,self.stock_location)
        quant_B=self.env['stock.quant']._gather(self.productB,self.stock_location)

        #ensurethatquantityforpickinghasbeenmoved
        self.assertFalse(sum(quant_A.mapped('quantity')))
        self.assertFalse(sum(quant_B.mapped('quantity')))

    deftest_batch_with_immediate_transfer_and_backorder_wizard_with_manual_operations(self):
        """Whenvalidatingabatchpickingwheresomepickingshavenoquantitiesdone+some
        do,thenavoidimmediatetransferswizardandremovepickingswithnoquantitiesdone
        fromthebatchpicking.Thiswillmakeitsouserscanvalidateapartiallydonebatch
        pickinginthiscase.
        """
        self.env['stock.quant']._update_available_quantity(self.productA,self.stock_location,5.0)
        self.env['stock.quant']._update_available_quantity(self.productB,self.stock_location,10.0)

        #Confirmbatch,pickingsshouldnotbeautomaticallyassigned.
        self.batch.action_confirm()
        self.assertEqual(self.picking_client_1.state,'confirmed','Picking1shouldbeconfirmed')
        self.assertEqual(self.picking_client_2.state,'confirmed','Picking2shouldbeconfirmed')
        #Asktoassign,sopickingsshouldbeassignednow.
        self.batch.action_assign()
        self.assertEqual(self.picking_client_1.state,'assigned','Picking1shouldbeready')
        self.assertEqual(self.picking_client_2.state,'assigned','Picking2shouldbeready')

        self.picking_client_1.move_lines.quantity_done=5
        #Thereshouldbeawizardaskingtomakeabackorder
        back_order_wizard_dict=self.batch.action_done()
        self.assertTrue(back_order_wizard_dict)
        self.assertEqual(back_order_wizard_dict.get('res_model'),'stock.backorder.confirmation')
        back_order_wizard=Form(self.env[(back_order_wizard_dict.get('res_model'))].with_context(back_order_wizard_dict['context'])).save()
        self.assertEqual(len(back_order_wizard.pick_ids),2)
        back_order_wizard.process()

        self.assertEqual(self.picking_client_1.state,'done','Picking1shouldbedone')
        self.assertEqual(self.picking_client_1.move_lines.product_uom_qty,5,'initialdemandshouldbe5afterpickingsplit')
        self.assertFalse(self.picking_client_2.batch_id,'Thepickingshouldberemovedfromthebatch')

    deftest_put_in_pack(self):
        self.env['stock.quant']._update_available_quantity(self.productA,self.stock_location,10.0)
        self.env['stock.quant']._update_available_quantity(self.productB,self.stock_location,10.0)

        #Confirmbatch,pickingsshouldnotbeautomaticallyassigned.
        self.batch.action_confirm()
        self.assertEqual(self.picking_client_1.state,'confirmed','Picking1shouldbeconfirmed')
        self.assertEqual(self.picking_client_2.state,'confirmed','Picking2shouldbeconfirmed')
        #Asktoassign,sopickingsshouldbeassignednow.
        self.batch.action_assign()
        self.assertEqual(self.picking_client_1.state,'assigned','Picking1shouldbeready')
        self.assertEqual(self.picking_client_2.state,'assigned','Picking2shouldbeready')

        #onlydopartofpickings+assigndifferentdestinations+trytopack(shouldgetwizardtocorrectdestination)
        self.batch.move_line_ids.qty_done=5
        self.batch.move_line_ids[0].location_dest_id=self.stock_location.id
        wizard_values=self.batch.action_put_in_pack()
        wizard=self.env[(wizard_values.get('res_model'))].browse(wizard_values.get('res_id'))
        wizard.location_dest_id=self.customer_location.id
        package=wizard.action_done()

        #anewpackageismadeanddonequantitiesshouldbeinsamepackage
        self.assertTrue(package)
        done_qty_move_lines=self.batch.move_line_ids.filtered(lambdaml:ml.qty_done==5)
        self.assertEqual(done_qty_move_lines[0].result_package_id.id,package.id)
        self.assertEqual(done_qty_move_lines[1].result_package_id.id,package.id)

        #notdonequantitiesshouldbesplitintoseparatelines
        self.assertEqual(len(self.batch.move_line_ids),4)

        #confirmw/backorder
        back_order_wizard_dict=self.batch.action_done()
        self.assertTrue(back_order_wizard_dict)
        back_order_wizard=Form(self.env[(back_order_wizard_dict.get('res_model'))].with_context(back_order_wizard_dict['context'])).save()
        self.assertEqual(len(back_order_wizard.pick_ids),2)
        back_order_wizard.process()

        #finalpackagelocationshouldbecorrectlysetbasedonwizard
        self.assertEqual(package.location_id.id,self.customer_location.id)


@tagged('-at_install','post_install')
classTestBatchPicking02(TransactionCase):

    defsetUp(self):
        super().setUp()
        self.stock_location=self.env.ref('stock.stock_location_stock')
        self.picking_type_internal=self.env.ref('stock.picking_type_internal')
        self.productA=self.env['product.product'].create({
            'name':'ProductA',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
        })
        self.productB=self.env['product.product'].create({
            'name':'ProductB',
            'type':'product',
            'categ_id':self.env.ref('product.product_category_all').id,
        })

    deftest_same_package_several_pickings(self):
        """
        Abatchwithtwotransfers,sourceanddestinationarethesame.The
        firstpickingcontains3xP,thesecondone7xP.The10Pareina
        package.Itshouldbepossibletotransferthewholepackageacrossthe
        twopickings
        """
        package=self.env['stock.quant.package'].create({
            'name':'superpackage',
        })

        loc1,loc2=self.stock_location.child_ids
        self.env['stock.quant']._update_available_quantity(self.productA,loc1,10,package_id=package)

        pickings=self.env['stock.picking'].create([{
            'location_id':loc1.id,
            'location_dest_id':loc2.id,
            'picking_type_id':self.picking_type_internal.id,
            'move_lines':[(0,0,{
                'name':'test_put_in_pack_from_multiple_pages',
                'location_id':loc1.id,
                'location_dest_id':loc2.id,
                'product_id':self.productA.id,
                'product_uom':self.productA.uom_id.id,
                'product_uom_qty':qty,
            })]
        }forqtyin(3,7)])
        pickings.action_confirm()
        pickings.action_assign()

        batch_form=Form(self.env['stock.picking.batch'])
        batch_form.picking_ids.add(pickings[0])
        batch_form.picking_ids.add(pickings[1])
        batch=batch_form.save()
        batch.action_confirm()

        pickings.move_line_ids[0].qty_done=3
        pickings.move_line_ids[1].qty_done=7
        pickings.move_line_ids.result_package_id=package

        batch.action_done()
        self.assertRecordValues(pickings.move_lines,[
            {'state':'done','quantity_done':3},
            {'state':'done','quantity_done':7},
        ])
        self.assertEqual(pickings.move_line_ids.result_package_id,package)


    deftest_batch_validation_without_backorder(self):
        loc1,loc2=self.stock_location.child_ids
        self.env['stock.quant']._update_available_quantity(self.productA,loc1,10)
        self.env['stock.quant']._update_available_quantity(self.productB,loc1,10)
        picking_1=self.env['stock.picking'].create({
            'location_id':loc1.id,
            'location_dest_id':loc2.id,
            'picking_type_id':self.picking_type_internal.id,
            'company_id':self.env.company.id,
        })
        self.env['stock.move'].create({
            'name':self.productA.name,
            'product_id':self.productA.id,
            'product_uom_qty':1,
            'product_uom':self.productA.uom_id.id,
            'picking_id':picking_1.id,
            'location_id':loc1.id,
            'location_dest_id':loc2.id,
        })

        picking_2=self.env['stock.picking'].create({
            'location_id':loc1.id,
            'location_dest_id':loc2.id,
            'picking_type_id':self.picking_type_internal.id,
            'company_id':self.env.company.id,
        })
        self.env['stock.move'].create({
            'name':self.productB.name,
            'product_id':self.productB.id,
            'product_uom_qty':5,
            'product_uom':self.productB.uom_id.id,
            'picking_id':picking_2.id,
            'location_id':loc1.id,
            'location_dest_id':loc2.id,
        })
        (picking_1|picking_2).action_confirm()
        (picking_1|picking_2).action_assign()
        picking_2.move_lines.move_line_ids.write({'qty_done':1})

        batch=self.env['stock.picking.batch'].create({
            'name':'Batch1',
            'company_id':self.env.company.id,
            'picking_ids':[(4,picking_1.id),(4,picking_2.id)]
        })
        batch.action_confirm()
        action=batch.action_done()
        Form(self.env[action['res_model']].with_context(action['context'])).save().process_cancel_backorder()
        self.assertEqual(batch.state,'done')
