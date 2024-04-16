#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportForm
fromflectra.addons.mrp.tests.commonimportTestMrpCommon
fromflectra.exceptionsimportUserError


classTestUnbuild(TestMrpCommon):
    defsetUp(self):
        super(TestUnbuild,self).setUp()
        self.stock_location=self.env.ref('stock.stock_location_stock')
        self.env.ref('base.group_user').write({
            'implied_ids':[(4,self.env.ref('stock.group_production_lot').id)]
        })

    deftest_unbuild_standart(self):
        """ThistestcreatesaMOandthencreates3unbuild
        ordersforthefinalproduct.Noneoftheproductsforthis
        testaretracked.Itchecksthestockstateaftereachorder
        andensureitiscorrect.
        """
        mo,bom,p_final,p1,p2=self.generate_mo()
        self.assertEqual(len(mo),1,'MOshouldhavebeencreated')

        self.env['stock.quant']._update_available_quantity(p1,self.stock_location,100)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location,5)
        mo.action_assign()

        mo_form=Form(mo)
        mo_form.qty_producing=5.0
        mo=mo_form.save()
        mo.button_mark_done()
        self.assertEqual(mo.state,'done',"Productionordershouldbeindonestate.")

        #Checkquantityinstockbeforeunbuild.
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p_final,self.stock_location),5,'Youshouldhavethe5finalproductinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p1,self.stock_location),80,'Youshouldhave80productsinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p2,self.stock_location),0,'Youshouldhaveconsumedallthe5productinstock')

        #---------------------------------------------------
        #      unbuild
        #---------------------------------------------------

        x=Form(self.env['mrp.unbuild'])
        x.product_id=p_final
        x.bom_id=bom
        x.product_qty=3
        x.save().action_unbuild()


        self.assertEqual(self.env['stock.quant']._get_available_quantity(p_final,self.stock_location),2,'Youshouldhaveconsumed3finalproductinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p1,self.stock_location),92,'Youshouldhave80productsinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p2,self.stock_location),3,'Youshouldhaveconsumedallthe5productinstock')

        x=Form(self.env['mrp.unbuild'])
        x.product_id=p_final
        x.bom_id=bom
        x.product_qty=2
        x.save().action_unbuild()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(p_final,self.stock_location),0,'Youshouldhave0finalproductinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p1,self.stock_location),100,'Youshouldhave80productsinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p2,self.stock_location),5,'Youshouldhaveconsumedallthe5productinstock')

        x=Form(self.env['mrp.unbuild'])
        x.product_id=p_final
        x.bom_id=bom
        x.product_qty=5
        x.save().action_unbuild()

        #Checkquantityinstockafterlastunbuild.
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p_final,self.stock_location,allow_negative=True),-5,'Youshouldhavenegativequantityforfinalproductinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p1,self.stock_location),120,'Youshouldhave80productsinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p2,self.stock_location),10,'Youshouldhaveconsumedallthe5productinstock')

    deftest_unbuild_with_final_lot(self):
        """ThistestcreatesaMOandthencreates3unbuild
        ordersforthefinalproduct.Onlythefinalproductistracked
        bylot.Itchecksthestockstateaftereachorder
        andensureitiscorrect.
        """
        mo,bom,p_final,p1,p2=self.generate_mo(tracking_final='lot')
        self.assertEqual(len(mo),1,'MOshouldhavebeencreated')

        lot=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':p_final.id,
            'company_id':self.env.company.id,
        })

        self.env['stock.quant']._update_available_quantity(p1,self.stock_location,100)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location,5)
        mo.action_assign()

        mo_form=Form(mo)
        mo_form.qty_producing=5.0
        mo_form.lot_producing_id=lot
        mo=mo_form.save()

        mo.button_mark_done()
        self.assertEqual(mo.state,'done',"Productionordershouldbeindonestate.")

        #Checkquantityinstockbeforeunbuild.
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p_final,self.stock_location,lot_id=lot),5,'Youshouldhavethe5finalproductinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p1,self.stock_location),80,'Youshouldhave80productsinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p2,self.stock_location),0,'Youshouldhaveconsumedallthe5productinstock')

        #---------------------------------------------------
        #      unbuild
        #---------------------------------------------------

        #Thisshouldfailsincewedonotchoosealottounbuildforfinalproduct.
        withself.assertRaises(AssertionError):
            x=Form(self.env['mrp.unbuild'])
            x.product_id=p_final
            x.bom_id=bom
            x.product_qty=3
            unbuild_order=x.save()

        x=Form(self.env['mrp.unbuild'])
        x.product_id=p_final
        x.bom_id=bom
        x.product_qty=3
        x.lot_id=lot
        x.save().action_unbuild()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(p_final,self.stock_location,lot_id=lot),2,'Youshouldhaveconsumed3finalproductinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p1,self.stock_location),92,'Youshouldhave80productsinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p2,self.stock_location),3,'Youshouldhaveconsumedallthe5productinstock')

        x=Form(self.env['mrp.unbuild'])
        x.product_id=p_final
        x.bom_id=bom
        x.product_qty=2
        x.lot_id=lot
        x.save().action_unbuild()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(p_final,self.stock_location,lot_id=lot),0,'Youshouldhave0finalproductinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p1,self.stock_location),100,'Youshouldhave80productsinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p2,self.stock_location),5,'Youshouldhaveconsumedallthe5productinstock')

        x=Form(self.env['mrp.unbuild'])
        x.product_id=p_final
        x.bom_id=bom
        x.product_qty=5
        x.lot_id=lot
        x.save().action_unbuild()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(p_final,self.stock_location,lot_id=lot,allow_negative=True),-5,'Youshouldhavenegativequantityforfinalproductinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p1,self.stock_location),120,'Youshouldhave80productsinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p2,self.stock_location),10,'Youshouldhaveconsumedallthe5productinstock')

    deftest_unbuild_with_comnsumed_lot(self):
        """ThistestcreatesaMOandthencreates3unbuild
        ordersforthefinalproduct.Onlyonceofthetwoconsumed
        productistrackedbylot.Itchecksthestockstateaftereach
        orderandensureitiscorrect.
        """
        mo,bom,p_final,p1,p2=self.generate_mo(tracking_base_1='lot')
        self.assertEqual(len(mo),1,'MOshouldhavebeencreated')

        lot=self.env['stock.production.lot'].create({
            'name':'lot1',
            'product_id':p1.id,
            'company_id':self.env.company.id,
        })

        self.env['stock.quant']._update_available_quantity(p1,self.stock_location,100,lot_id=lot)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location,5)
        mo.action_assign()
        formlinmo.move_raw_ids.mapped('move_line_ids'):
            ifml.product_id.tracking!='none':
                self.assertEqual(ml.lot_id,lot,'Wrongreservedlot.')

        #FIXMEsle:behaviorchange
        mo_form=Form(mo)
        mo_form.qty_producing=5.0
        mo=mo_form.save()
        details_operation_form=Form(mo.move_raw_ids[1],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.edit(0)asml:
            ml.lot_id=lot
            ml.qty_done=20
        details_operation_form.save()

        mo.button_mark_done()
        self.assertEqual(mo.state,'done',"Productionordershouldbeindonestate.")
        #Checkquantityinstockbeforeunbuild.
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p_final,self.stock_location),5,'Youshouldhavethe5finalproductinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p1,self.stock_location,lot_id=lot),80,'Youshouldhave80productsinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p2,self.stock_location),0,'Youshouldhaveconsumedallthe5productinstock')

        #---------------------------------------------------
        #      unbuild
        #---------------------------------------------------

        x=Form(self.env['mrp.unbuild'])
        x.product_id=p_final
        x.bom_id=bom
        x.product_qty=3
        unbuild_order=x.save()

        #ThisshouldfailsincewedonotprovidetheMOthatwewantedtounbuild.(withoutMOwedonotknowwhichconsumedlotwehavetorestore)
        withself.assertRaises(UserError):
            unbuild_order.action_unbuild()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(p_final,self.stock_location),5,'Youshouldhaveconsumed3finalproductinstock')

        unbuild_order.mo_id=mo.id
        unbuild_order.action_unbuild()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(p_final,self.stock_location),2,'Youshouldhaveconsumed3finalproductinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p1,self.stock_location,lot_id=lot),92,'Youshouldhave92productsinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p2,self.stock_location),3,'Youshouldhaveconsumedallthe5productinstock')

        x=Form(self.env['mrp.unbuild'])
        x.product_id=p_final
        x.bom_id=bom
        x.mo_id=mo
        x.product_qty=2
        x.save().action_unbuild()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(p_final,self.stock_location),0,'Youshouldhave0finalproductinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p1,self.stock_location,lot_id=lot),100,'Youshouldhave80productsinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p2,self.stock_location),5,'Youshouldhaveconsumedallthe5productinstock')

        x=Form(self.env['mrp.unbuild'])
        x.product_id=p_final
        x.bom_id=bom
        x.mo_id=mo
        x.product_qty=5
        x.save().action_unbuild()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(p_final,self.stock_location,allow_negative=True),-5,'Youshouldhavenegativequantityforfinalproductinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p1,self.stock_location,lot_id=lot),120,'Youshouldhave80productsinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p2,self.stock_location),10,'Youshouldhaveconsumedallthe5productinstock')

    deftest_unbuild_with_everything_tracked(self):
        """ThistestcreatesaMOandthencreates3unbuild
        ordersforthefinalproduct.Alltheproductsforthis
        testaretracked.Itchecksthestockstateaftereachorder
        andensureitiscorrect.
        """
        mo,bom,p_final,p1,p2=self.generate_mo(tracking_final='lot',tracking_base_2='lot',tracking_base_1='lot')
        self.assertEqual(len(mo),1,'MOshouldhavebeencreated')

        lot_final=self.env['stock.production.lot'].create({
            'name':'lot_final',
            'product_id':p_final.id,
            'company_id':self.env.company.id,
        })
        lot_1=self.env['stock.production.lot'].create({
            'name':'lot_consumed_1',
            'product_id':p1.id,
            'company_id':self.env.company.id,
        })
        lot_2=self.env['stock.production.lot'].create({
            'name':'lot_consumed_2',
            'product_id':p2.id,
            'company_id':self.env.company.id,
        })

        self.env['stock.quant']._update_available_quantity(p1,self.stock_location,100,lot_id=lot_1)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location,5,lot_id=lot_2)
        mo.action_assign()

        #FIXMEsle:behaviorchange
        mo_form=Form(mo)
        mo_form.qty_producing=5.0
        mo_form.lot_producing_id=lot_final
        mo=mo_form.save()
        details_operation_form=Form(mo.move_raw_ids[0],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.edit(0)asml:
            ml.qty_done=5
        details_operation_form.save()
        details_operation_form=Form(mo.move_raw_ids[1],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.edit(0)asml:
            ml.qty_done=20
        details_operation_form.save()

        mo.button_mark_done()
        self.assertEqual(mo.state,'done',"Productionordershouldbeindonestate.")
        #Checkquantityinstockbeforeunbuild.
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p_final,self.stock_location,lot_id=lot_final),5,'Youshouldhavethe5finalproductinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p1,self.stock_location,lot_id=lot_1),80,'Youshouldhave80productsinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p2,self.stock_location,lot_id=lot_2),0,'Youshouldhaveconsumedallthe5productinstock')

        #---------------------------------------------------
        #      unbuild
        #---------------------------------------------------

        x=Form(self.env['mrp.unbuild'])
        withself.assertRaises(AssertionError):
            x.product_id=p_final
            x.bom_id=bom
            x.product_qty=3
            x.save()

        withself.assertRaises(AssertionError):
            x.product_id=p_final
            x.bom_id=bom
            x.product_qty=3
            x.save()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(p_final,self.stock_location,lot_id=lot_final),5,'Youshouldhaveconsumed3finalproductinstock')

        withself.assertRaises(AssertionError):
            x.product_id=p_final
            x.bom_id=bom
            x.mo_id=mo
            x.product_qty=3
            x.save()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(p_final,self.stock_location,lot_id=lot_final),5,'Youshouldhaveconsumed3finalproductinstock')

        x=Form(self.env['mrp.unbuild'])
        x.product_id=p_final
        x.bom_id=bom
        x.mo_id=mo
        x.product_qty=3
        x.lot_id=lot_final
        x.save().action_unbuild()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(p_final,self.stock_location,lot_id=lot_final),2,'Youshouldhaveconsumed3finalproductinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p1,self.stock_location,lot_id=lot_1),92,'Youshouldhave92productsinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p2,self.stock_location,lot_id=lot_2),3,'Youshouldhaveconsumedallthe5productinstock')

        x=Form(self.env['mrp.unbuild'])
        x.product_id=p_final
        x.bom_id=bom
        x.mo_id=mo
        x.product_qty=2
        x.lot_id=lot_final
        x.save().action_unbuild()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(p_final,self.stock_location,lot_id=lot_final),0,'Youshouldhave0finalproductinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p1,self.stock_location,lot_id=lot_1),100,'Youshouldhave80productsinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p2,self.stock_location,lot_id=lot_2),5,'Youshouldhaveconsumedallthe5productinstock')

        x=Form(self.env['mrp.unbuild'])
        x.product_id=p_final
        x.bom_id=bom
        x.mo_id=mo
        x.product_qty=5
        x.lot_id=lot_final
        x.save().action_unbuild()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(p_final,self.stock_location,lot_id=lot_final,allow_negative=True),-5,'Youshouldhavenegativequantityforfinalproductinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p1,self.stock_location,lot_id=lot_1),120,'Youshouldhave80productsinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p2,self.stock_location,lot_id=lot_2),10,'Youshouldhaveconsumedallthe5productinstock')

    deftest_unbuild_with_duplicate_move(self):
        """ThistestcreatesaMOfrom3differentlotonaconsumedproduct(p2).
        Theunbuildordershouldrevertthecorrectquantityforeachspecificlot.
        """
        mo,bom,p_final,p1,p2=self.generate_mo(tracking_final='none',tracking_base_2='lot',tracking_base_1='none')
        self.assertEqual(len(mo),1,'MOshouldhavebeencreated')

        lot_1=self.env['stock.production.lot'].create({
            'name':'lot_1',
            'product_id':p2.id,
            'company_id':self.env.company.id,
        })
        lot_2=self.env['stock.production.lot'].create({
            'name':'lot_2',
            'product_id':p2.id,
            'company_id':self.env.company.id,
        })
        lot_3=self.env['stock.production.lot'].create({
            'name':'lot_3',
            'product_id':p2.id,
            'company_id':self.env.company.id,
        })
        self.env['stock.quant']._update_available_quantity(p1,self.stock_location,100)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location,1,lot_id=lot_1)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location,3,lot_id=lot_2)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location,2,lot_id=lot_3)
        mo.action_assign()

        mo_form=Form(mo)
        mo_form.qty_producing=5.0
        mo=mo_form.save()
        details_operation_form=Form(mo.move_raw_ids.filtered(lambdaml:ml.product_id==p2),view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.edit(0)asml:
            ml.qty_done=ml.product_uom_qty
        withdetails_operation_form.move_line_ids.edit(1)asml:
            ml.qty_done=ml.product_uom_qty
        withdetails_operation_form.move_line_ids.edit(2)asml:
            ml.qty_done=ml.product_uom_qty
        details_operation_form.save()

        mo.button_mark_done()
        self.assertEqual(mo.state,'done',"Productionordershouldbeindonestate.")
        #Checkquantityinstockbeforeunbuild.
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p_final,self.stock_location),5,'Youshouldhavethe5finalproductinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p1,self.stock_location),80,'Youshouldhave80productsinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p2,self.stock_location,lot_id=lot_1),0,'Youshouldhaveconsumedallthe1productforlot1instock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p2,self.stock_location,lot_id=lot_2),0,'Youshouldhaveconsumedallthe3productforlot2instock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p2,self.stock_location,lot_id=lot_3),1,'Youshouldhaveconsumedonly1productforlot3instock')

        x=Form(self.env['mrp.unbuild'])
        x.product_id=p_final
        x.bom_id=bom
        x.mo_id=mo
        x.product_qty=5
        x.save().action_unbuild()

        self.assertEqual(self.env['stock.quant']._get_available_quantity(p_final,self.stock_location),0,'Youshouldhavenomorefinalproductinstockafterunbuild')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p1,self.stock_location),100,'Youshouldhave80productsinstock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p2,self.stock_location,lot_id=lot_1),1,'Youshouldhavegetyourproductwithlot1instock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p2,self.stock_location,lot_id=lot_2),3,'Youshouldhavethe3basicproductforlot2instock')
        self.assertEqual(self.env['stock.quant']._get_available_quantity(p2,self.stock_location,lot_id=lot_3),2,'Youshouldhavegetoneproductbackforlot3')

    deftest_production_links_with_non_tracked_lots(self):
        """ThistestproducesanMOintwotimesandchecksthatthemovelinesarelinkedinacorrectway
        """
        mo,bom,p_final,p1,p2=self.generate_mo(tracking_final='lot',tracking_base_1='none',tracking_base_2='lot')
        #YoungTom
        #   \Botox-4-p1
        #   \OldTom-1-p2
        lot_1=self.env['stock.production.lot'].create({
            'name':'lot_1',
            'product_id':p2.id,
            'company_id':self.env.company.id,
        })

        self.env['stock.quant']._update_available_quantity(p2,self.stock_location,3,lot_id=lot_1)
        lot_finished_1=self.env['stock.production.lot'].create({
            'name':'lot_finished_1',
            'product_id':p_final.id,
            'company_id':self.env.company.id,
        })

        self.assertEqual(mo.product_qty,5)
        mo_form=Form(mo)
        mo_form.qty_producing=3.0
        mo_form.lot_producing_id=lot_finished_1
        mo=mo_form.save()
        self.assertEqual(mo.move_raw_ids[1].quantity_done,12)
        details_operation_form=Form(mo.move_raw_ids[0],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.new()asml:
            ml.qty_done=3
            ml.lot_id=lot_1
        details_operation_form.save()
        action=mo.button_mark_done()
        backorder=Form(self.env[action['res_model']].with_context(**action['context']))
        backorder.save().action_backorder()

        lot_2=self.env['stock.production.lot'].create({
            'name':'lot_2',
            'product_id':p2.id,
            'company_id':self.env.company.id,
        })

        self.env['stock.quant']._update_available_quantity(p2,self.stock_location,4,lot_id=lot_2)
        lot_finished_2=self.env['stock.production.lot'].create({
            'name':'lot_finished_2',
            'product_id':p_final.id,
            'company_id':self.env.company.id,
        })

        mo=mo.procurement_group_id.mrp_production_ids[1]
        #FIXMEsle:issueinbackorder?
        mo.move_raw_ids.move_line_ids.unlink()
        self.assertEqual(mo.product_qty,2)
        mo_form=Form(mo)
        mo_form.qty_producing=2
        mo_form.lot_producing_id=lot_finished_2
        mo=mo_form.save()
        details_operation_form=Form(mo.move_raw_ids[0],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.new()asml:
            ml.qty_done=2
            ml.lot_id=lot_2
        details_operation_form.save()
        action=mo.button_mark_done()

        mo1=mo.procurement_group_id.mrp_production_ids[0]
        ml=mo1.finished_move_line_ids[0].consume_line_ids.filtered(lambdam:m.product_id==p1andlot_finished_1inm.produce_line_ids.lot_id)
        self.assertEqual(sum(ml.mapped('qty_done')),12.0,'Shouldhaveconsumed12forthefirstlot')
        ml=mo.finished_move_line_ids[0].consume_line_ids.filtered(lambdam:m.product_id==p1andlot_finished_2inm.produce_line_ids.lot_id)
        self.assertEqual(sum(ml.mapped('qty_done')),8.0,'Shouldhaveconsumed8forthesecondlot')

    deftest_unbuild_with_routes(self):
        """ThistestcreatesaMOofastockableproduct(Table).AnewrouteforruleQC/Unbuild->Stock
        iscreatedwithWarehouse->True.
        TheunbuildordershouldreverttheconsumedcomponentsintoQC/Unbuildlocationforqualitycheck
        andthenapickingshouldbegeneratedfortransferringcomponentsfromQC/Unbuildlocationtostock.
        """
        StockQuant=self.env['stock.quant']
        ProductObj=self.env['product.product']
        #CreatenewQC/Unbuildlocation
        warehouse=self.env.ref('stock.warehouse0')
        unbuild_location=self.env['stock.location'].create({
            'name':'QC/Unbuild',
            'usage':'internal',
            'location_id':warehouse.view_location_id.id
        })

        #CreateaproductroutecontainingastockrulethatwillmoveproductfromQC/Unbuildlocationtostock
        product_route=self.env['stock.location.route'].create({
            'name':'QC/Unbuild->Stock',
            'warehouse_selectable':True,
            'warehouse_ids':[(4,warehouse.id)],
            'rule_ids':[(0,0,{
                'name':'SendMatrialQC/Unbuild->Stock',
                'action':'push',
                'picking_type_id':self.ref('stock.picking_type_internal'),
                'location_src_id':unbuild_location.id,
                'location_id':self.stock_location.id,
            })],
        })

        #Createastockableproductanditscomponents
        finshed_product=ProductObj.create({
            'name':'Table',
            'type':'product',
        })
        component1=ProductObj.create({
            'name':'Tablehead',
            'type':'product',
        })
        component2=ProductObj.create({
            'name':'Tablestand',
            'type':'product',
        })

        #Createbomandaddcomponents
        bom=self.env['mrp.bom'].create({
            'product_id':finshed_product.id,
            'product_tmpl_id':finshed_product.product_tmpl_id.id,
            'product_uom_id':self.uom_unit.id,
            'product_qty':1.0,
            'type':'normal',
            'bom_line_ids':[
                (0,0,{'product_id':component1.id,'product_qty':1}),
                (0,0,{'product_id':component2.id,'product_qty':1})
            ]})

        #Setonhandquantity
        StockQuant._update_available_quantity(component1,self.stock_location,1)
        StockQuant._update_available_quantity(component2,self.stock_location,1)

        #Createmo
        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=finshed_product
        mo_form.bom_id=bom
        mo_form.product_uom_id=finshed_product.uom_id
        mo_form.product_qty=1.0
        mo=mo_form.save()
        self.assertEqual(len(mo),1,'MOshouldhavebeencreated')
        mo.action_confirm()
        mo.action_assign()

        #Producethefinalproduct
        mo_form=Form(mo)
        mo_form.qty_producing=1.0
        produce_wizard=mo_form.save()

        mo.button_mark_done()
        self.assertEqual(mo.state,'done',"Productionordershouldbeindonestate.")

        #Checkquantityinstockbeforeunbuild
        self.assertEqual(StockQuant._get_available_quantity(finshed_product,self.stock_location),1,'Tableshouldbeavailableinstock')
        self.assertEqual(StockQuant._get_available_quantity(component1,self.stock_location),0,'Tableheadshouldnotbeavailableinstock')
        self.assertEqual(StockQuant._get_available_quantity(component2,self.stock_location),0,'Tablestandshouldnotbeavailableinstock')

        #---------------------------------------------------
        #      Unbuild
        #---------------------------------------------------

        #Createanunbuildorderofthefinishedproductandsetthedestinationloacation=QC/Unbuild
        x=Form(self.env['mrp.unbuild'])
        x.product_id=finshed_product
        x.bom_id=bom
        x.mo_id=mo
        x.product_qty=1
        x.location_id=self.stock_location
        x.location_dest_id=unbuild_location
        x.save().action_unbuild()

        #Checktheavailablequantityofcomponentsandfinalproductinstock
        self.assertEqual(StockQuant._get_available_quantity(finshed_product,self.stock_location),0,'Tableshouldnotbeavailableinstockasitisunbuild')
        self.assertEqual(StockQuant._get_available_quantity(component1,self.stock_location),0,'TableheadshouldnotbeavailableinstockasitisinQC/Unbuildlocation')
        self.assertEqual(StockQuant._get_available_quantity(component2,self.stock_location),0,'TablestandshouldnotbeavailableinstockasitisinQC/Unbuildlocation')

        #Findnewgeneratedpicking
        picking=self.env['stock.picking'].search([('product_id','in',[component1.id,component2.id])])
        self.assertEqual(picking.location_id.id,unbuild_location.id,'Wrongsourcelocationinpicking')
        self.assertEqual(picking.location_dest_id.id,self.stock_location.id,'Wrongdestinationlocationinpicking')

        #Transferit
        formlinpicking.move_ids_without_package:
            ml.quantity_done=1
        picking._action_done()

        #Checktheavailablequantityofcomponentsandfinalproductinstock
        self.assertEqual(StockQuant._get_available_quantity(finshed_product,self.stock_location),0,'Tableshouldnotbeavailableinstock')
        self.assertEqual(StockQuant._get_available_quantity(component1,self.stock_location),1,'Tableheadshouldbeavailableinstockasthepickingistransferred')
        self.assertEqual(StockQuant._get_available_quantity(component2,self.stock_location),1,'Tablestandshouldbeavailableinstockasthepickingistransferred')

    deftest_unbuild_decimal_qty(self):
        """
        Usecase:
        -decimalaccuracyofProductUoM>decimalaccuracyofUnits
        -unbuildaproductwithadecimalquantityofcomponent
        """
        self.env['decimal.precision'].search([('name','=','ProductUnitofMeasure')]).digits=4
        self.uom_unit.rounding=0.001

        self.bom_1.product_qty=3
        self.bom_1.bom_line_ids.product_qty=5
        self.env['stock.quant']._update_available_quantity(self.product_2,self.stock_location,3)

        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=self.bom_1.product_id
        mo_form.bom_id=self.bom_1
        mo=mo_form.save()
        mo.action_confirm()
        mo.action_assign()

        mo_form=Form(mo)
        mo_form.qty_producing=3
        mo_form.save()
        mo.button_mark_done()

        uo_form=Form(self.env['mrp.unbuild'])
        uo_form.mo_id=mo
        #Unbuildingoneproductmeansadecimalquantityequalto1/3*5foreachcomponent
        uo_form.product_qty=1
        uo=uo_form.save()
        uo.action_unbuild()
        self.assertEqual(uo.state,'done')

    deftest_unbuild_similar_tracked_components(self):
        """
        SupposeaMOwith,inthecomponents,twolinesforthesametracked-by-usnproduct
        WhenunbuildingsuchanMO,allSNusedintheMOshouldbebackinstock
        """
        compo,finished=self.env['product.product'].create([{
            'name':'compo',
            'type':'product',
            'tracking':'serial',
        },{
            'name':'finished',
            'type':'product',
        }])

        lot01,lot02=self.env['stock.production.lot'].create([{
            'name':n,
            'product_id':compo.id,
            'company_id':self.env.company.id,
        }fornin['lot01','lot02']])
        self.env['stock.quant']._update_available_quantity(compo,self.stock_location,1,lot_id=lot01)
        self.env['stock.quant']._update_available_quantity(compo,self.stock_location,1,lot_id=lot02)

        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=finished
        withmo_form.move_raw_ids.new()asline:
            line.product_id=compo
            line.product_uom_qty=1
        withmo_form.move_raw_ids.new()asline:
            line.product_id=compo
            line.product_uom_qty=1
        mo=mo_form.save()

        mo.action_confirm()
        mo_form=Form(mo)
        mo_form.qty_producing=1
        mo=mo_form.save()
        mo.action_assign()

        details_operation_form=Form(mo.move_raw_ids[0],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.edit(0)asml:
            ml.qty_done=1
        details_operation_form.save()
        details_operation_form=Form(mo.move_raw_ids[1],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.edit(0)asml:
            ml.qty_done=1
        details_operation_form.save()
        mo.button_mark_done()

        uo_form=Form(self.env['mrp.unbuild'])
        uo_form.mo_id=mo
        uo_form.product_qty=1
        uo=uo_form.save()
        uo.action_unbuild()

        self.assertEqual(uo.produce_line_ids.filtered(lambdasm:sm.product_id==compo).lot_ids,lot01+lot02)

    deftest_unbuild_and_multilocations(self):
        """
        Basicflow:producep_final,transferittoasub-locationandthen
        unbuildit.Thetestensuresthatthesource/destinationlocationsofan
        unbuildorderareappliedonthestockmoves
        """
        grp_multi_loc=self.env.ref('stock.group_stock_multi_locations')
        self.env.user.write({'groups_id':[(4,grp_multi_loc.id,0)]})
        warehouse=self.env['stock.warehouse'].search([('company_id','=',self.env.user.id)],limit=1)
        prod_location=self.env['stock.location'].search([('usage','=','production'),('company_id','=',self.env.user.id)])
        subloc01,subloc02,=self.stock_location.child_ids[:2]

        mo,_,p_final,p1,p2=self.generate_mo(qty_final=1,qty_base_1=1,qty_base_2=1)

        self.env['stock.quant']._update_available_quantity(p1,self.stock_location,1)
        self.env['stock.quant']._update_available_quantity(p2,self.stock_location,1)
        mo.action_assign()

        mo_form=Form(mo)
        mo_form.qty_producing=1.0
        mo=mo_form.save()
        mo.button_mark_done()

        #TransferthefinishedproductfromWH/Stockto`subloc01`
        internal_form=Form(self.env['stock.picking'])
        internal_form.picking_type_id=warehouse.int_type_id
        internal_form.location_id=self.stock_location
        internal_form.location_dest_id=subloc01
        withinternal_form.move_ids_without_package.new()asmove:
            move.product_id=p_final
            move.product_uom_qty=1.0
        internal_transfer=internal_form.save()
        internal_transfer.action_confirm()
        internal_transfer.action_assign()
        internal_transfer.move_line_ids.qty_done=1.0
        internal_transfer.button_validate()

        unbuild_order_form=Form(self.env['mrp.unbuild'])
        unbuild_order_form.mo_id=mo
        unbuild_order_form.location_id=subloc01
        unbuild_order_form.location_dest_id=subloc02
        unbuild_order=unbuild_order_form.save()
        unbuild_order.action_unbuild()

        self.assertRecordValues(unbuild_order.produce_line_ids,[
            #pylint:disable=bad-whitespace
            {'product_id':p_final.id, 'location_id':subloc01.id,        'location_dest_id':prod_location.id},
            {'product_id':p2.id,      'location_id':prod_location.id,   'location_dest_id':subloc02.id},
            {'product_id':p1.id,      'location_id':prod_location.id,   'location_dest_id':subloc02.id},
        ])

    deftest_use_unbuilt_sn_in_mo(self):
        """
            useanunbuiltserialnumberinmanufacturingorder:
            produceatrackedproduct,unbuilditandthenuseitasacomponentwiththesameSNinamo.
        """
        product_1=self.env['product.product'].create({
            'name':'Producttrackedbysn',
            'type':'product',
            'tracking':'serial',
        })
        product_1_sn=self.env['stock.production.lot'].create({
            'product_id':product_1.id,
            'company_id':self.env.company.id})
        component=self.env['product.product'].create({
            'name':'Productcomponent',
            'type':'product',
        })
        bom_1=self.env['mrp.bom'].create({
            'product_id':product_1.id,
            'product_tmpl_id':product_1.product_tmpl_id.id,
            'product_uom_id':self.env.ref('uom.product_uom_unit').id,
            'product_qty':1.0,
            'type':'normal',
            'bom_line_ids':[
                (0,0,{'product_id':component.id,'product_qty':1}),
            ],
        })
        product_2=self.env['product.product'].create({
            'name':'finishedProduct',
            'type':'product',
        })
        self.env['mrp.bom'].create({
            'product_id':product_2.id,
            'product_tmpl_id':product_2.product_tmpl_id.id,
            'product_uom_id':self.env.ref('uom.product_uom_unit').id,
            'product_qty':1.0,
            'type':'normal',
            'bom_line_ids':[
                (0,0,{'product_id':product_1.id,'product_qty':1}),
            ],
        })
        #mo1
        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=product_1
        mo_form.bom_id=bom_1
        mo_form.product_qty=1.0
        mo=mo_form.save()
        mo.action_confirm()

        mo_form=Form(mo)
        mo_form.qty_producing=1.0
        mo_form.lot_producing_id=product_1_sn
        mo=mo_form.save()
        mo.button_mark_done()
        self.assertEqual(mo.state,'done',"Productionordershouldbeindonestate.")

        #unbuildorder
        unbuild_form=Form(self.env['mrp.unbuild'])
        unbuild_form.mo_id=mo
        unbuild_form.lot_id=product_1_sn
        unbuild_form.save().action_unbuild()

        #mo2
        mo_form=Form(self.env['mrp.production'])
        mo_form.product_id=product_2
        mo2=mo_form.save()
        mo2.action_confirm()
        details_operation_form=Form(mo2.move_raw_ids[0],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.new()asml:
            ml.lot_id=product_1_sn
            ml.qty_done=1
        details_operation_form.save()
        mo_form=Form(mo2)
        mo_form.qty_producing=1
        mo2=mo_form.save()
        mo2.button_mark_done()
        self.assertEqual(mo2.state,'done',"Productionordershouldbeindonestate.")
