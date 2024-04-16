#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportForm
fromflectra.testsimportcommon


classTestMrpByProduct(common.TransactionCase):

    defsetUp(self):
        super(TestMrpByProduct,self).setUp()
        self.MrpBom=self.env['mrp.bom']
        self.warehouse=self.env.ref('stock.warehouse0')
        route_manufacture=self.warehouse.manufacture_pull_id.route_id.id
        route_mto=self.warehouse.mto_pull_id.route_id.id
        self.uom_unit_id=self.ref('uom.product_uom_unit')
        defcreate_product(name,route_ids=[]):
            returnself.env['product.product'].create({
                'name':name,
                'type':'product',
                'route_ids':route_ids})

        #CreateproductA,B,C.
        #--------------------------
        self.product_a=create_product('ProductA',route_ids=[(6,0,[route_manufacture,route_mto])])
        self.product_b=create_product('ProductB',route_ids=[(6,0,[route_manufacture,route_mto])])
        self.product_c_id=create_product('ProductC',route_ids=[]).id

    deftest_00_mrp_byproduct(self):
        """Testbyproductwithproductionorder."""
        #CreateBOMforproductB
        #------------------------
        bom_product_b=self.MrpBom.create({
            'product_tmpl_id':self.product_b.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'normal',
            'product_uom_id':self.uom_unit_id,
            'bom_line_ids':[(0,0,{'product_id':self.product_c_id,'product_uom_id':self.uom_unit_id,'product_qty':2})]
            })

        #CreateBOMforproductAandsetbyproductproductB
        bom_product_a=self.MrpBom.create({
            'product_tmpl_id':self.product_a.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'normal',
            'product_uom_id':self.uom_unit_id,
            'bom_line_ids':[(0,0,{'product_id':self.product_c_id,'product_uom_id':self.uom_unit_id,'product_qty':2})],
            'byproduct_ids':[(0,0,{'product_id':self.product_b.id,'product_uom_id':self.uom_unit_id,'product_qty':1})]
            })

        #CreateproductionorderforproductA
        #-------------------------------------

        mnf_product_a_form=Form(self.env['mrp.production'])
        mnf_product_a_form.product_id=self.product_a
        mnf_product_a_form.bom_id=bom_product_a
        mnf_product_a_form.product_qty=2.0
        mnf_product_a=mnf_product_a_form.save()
        mnf_product_a.action_confirm()

        #Iconfirmtheproductionorder.
        self.assertEqual(mnf_product_a.state,'confirmed','Productionordershouldbeinstateconfirmed')

        #NowIcheckthestockmovesforthebyproductIcreatedinthebillofmaterial.
        #ThismoveiscreatedautomaticallywhenIconfirmedtheproductionorder.
        moves=mnf_product_a.move_raw_ids|mnf_product_a.move_finished_ids
        self.assertTrue(moves,'Nomovesarecreated!')

        #Iconsumeandproducetheproductionofproducts.
        #Icreaterecordforselectingmodeandquantityofproductstoproduce.
        mo_form=Form(mnf_product_a)
        mo_form.qty_producing=2.00
        mnf_product_a=mo_form.save()
        #Ifinishtheproductionorder.
        self.assertEqual(len(mnf_product_a.move_raw_ids),1,"Wrongconsumemoveonproductionorder.")
        consume_move_c=mnf_product_a.move_raw_ids
        by_product_move=mnf_product_a.move_finished_ids.filtered(lambdax:x.product_id.id==self.product_b.id)
        #Checksubproductionproducedquantity...
        self.assertEqual(consume_move_c.product_uom_qty,4,"Wrongconsumedquantityofproductc.")
        self.assertEqual(by_product_move.product_uom_qty,2,"Wrongproducedquantityofsubproduct.")

        mnf_product_a._post_inventory()

        #IseethatstockmovesofExternalHardDiskincludingHeadsetUSBaredonenow.
        self.assertFalse(any(move.state!='done'formoveinmoves),'Movesarenotdone!')

    deftest_01_mrp_byproduct(self):
        self.env["stock.quant"].create({
            "product_id":self.product_c_id,
            "location_id":self.warehouse.lot_stock_id.id,
            "quantity":4,
        })
        bom_product_a=self.MrpBom.create({
            'product_tmpl_id':self.product_a.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'normal',
            'product_uom_id':self.uom_unit_id,
            'bom_line_ids':[(0,0,{'product_id':self.product_c_id,'product_uom_id':self.uom_unit_id,'product_qty':2})]
            })
        mnf_product_a_form=Form(self.env['mrp.production'])
        mnf_product_a_form.product_id=self.product_a
        mnf_product_a_form.bom_id=bom_product_a
        mnf_product_a_form.product_qty=2.0
        mnf_product_a=mnf_product_a_form.save()
        mnf_product_a.action_confirm()
        self.assertEqual(mnf_product_a.state,"confirmed")
        mnf_product_a.move_raw_ids._action_assign()
        mnf_product_a.move_raw_ids.quantity_done=mnf_product_a.move_raw_ids.product_uom_qty
        mnf_product_a.move_raw_ids._action_done()
        self.assertEqual(mnf_product_a.state,"progress")
        mnf_product_a.qty_producing=2
        mnf_product_a.button_mark_done()
        self.assertTrue(mnf_product_a.move_finished_ids)
        self.assertEqual(mnf_product_a.state,"done")

    deftest_change_product(self):
        """CreateaproductionorderforaspecificproductwithaBoM.ThenchangetheBoMandthefinishedproductfor
        otheronesandcheckthefinishedproductofthefirstmodidnotbecameabyproductofthesecondone."""
        #CreateBOMforproductAwithproductBascomponent
        bom_product_a=self.MrpBom.create({
            'product_tmpl_id':self.product_a.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'normal',
            'product_uom_id':self.uom_unit_id,
            'bom_line_ids':[(0,0,{'product_id':self.product_b.id,'product_uom_id':self.uom_unit_id,'product_qty':2})],
            })

        bom_product_a_2=self.MrpBom.create({
            'product_tmpl_id':self.product_b.product_tmpl_id.id,
            'product_qty':1.0,
            'type':'normal',
            'product_uom_id':self.uom_unit_id,
            'bom_line_ids':[(0,0,{'product_id':self.product_c_id,'product_uom_id':self.uom_unit_id,'product_qty':2})],
            })
        #CreateproductionorderforproductA
        #-------------------------------------

        mnf_product_a_form=Form(self.env['mrp.production'])
        mnf_product_a_form.product_id=self.product_a
        mnf_product_a_form.bom_id=bom_product_a
        mnf_product_a_form.product_qty=1.0
        mnf_product_a=mnf_product_a_form.save()
        mnf_product_a_form=Form(mnf_product_a)
        mnf_product_a_form.bom_id=bom_product_a_2
        mnf_product_a=mnf_product_a_form.save()
        self.assertEqual(mnf_product_a.move_raw_ids.product_id.id,self.product_c_id)
        self.assertFalse(mnf_product_a.move_byproduct_ids)
