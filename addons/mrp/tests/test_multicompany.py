#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportcommon,Form
fromflectra.exceptionsimportUserError


classTestMrpMulticompany(common.TransactionCase):

    defsetUp(self):
        super(TestMrpMulticompany,self).setUp()

        group_user=self.env.ref('base.group_user')
        group_mrp_manager=self.env.ref('mrp.group_mrp_manager')
        self.company_a=self.env['res.company'].create({'name':'CompanyA'})
        self.company_b=self.env['res.company'].create({'name':'CompanyB'})
        self.warehouse_a=self.env['stock.warehouse'].search([('company_id','=',self.company_a.id)],limit=1)
        self.warehouse_b=self.env['stock.warehouse'].search([('company_id','=',self.company_b.id)],limit=1)
        self.stock_location_a=self.warehouse_a.lot_stock_id
        self.stock_location_b=self.warehouse_b.lot_stock_id

        self.user_a=self.env['res.users'].create({
            'name':'usercompanyawithaccesstocompanyb',
            'login':'usera',
            'groups_id':[(6,0,[group_user.id,group_mrp_manager.id])],
            'company_id':self.company_a.id,
            'company_ids':[(6,0,[self.company_a.id,self.company_b.id])]
        })
        self.user_b=self.env['res.users'].create({
            'name':'usercompanyawithaccesstocompanyb',
            'login':'userb',
            'groups_id':[(6,0,[group_user.id,group_mrp_manager.id])],
            'company_id':self.company_b.id,
            'company_ids':[(6,0,[self.company_a.id,self.company_b.id])]
        })

    deftest_bom_1(self):
        """CheckitisnotpossibletouseaproductofCompanyBina
        bomofCompanyA."""

        product_b=self.env['product.product'].create({
            'name':'p1',
            'company_id':self.company_b.id,
        })
        withself.assertRaises(UserError):
            self.env['mrp.bom'].create({
                'product_id':product_b.id,
                'product_tmpl_id':product_b.product_tmpl_id.id,
                'company_id':self.company_a.id,
            })

    deftest_bom_2(self):
        """CheckitisnotpossibletouseaproductofCompanyBasacomponent
        inabomofCompanyA."""

        product_a=self.env['product.product'].create({
            'name':'p1',
            'company_id':self.company_a.id,
        })
        product_b=self.env['product.product'].create({
            'name':'p2',
            'company_id':self.company_b.id,
        })
        withself.assertRaises(UserError):
            self.env['mrp.bom'].create({
                'product_id':product_a.id,
                'product_tmpl_id':product_b.product_tmpl_id.id,
                'company_id':self.company_a.id,
                'bom_line_ids':[(0,0,{'product_id':product_b.id})]
            })

    deftest_production_1(self):
        """CheckitisnotpossibletoconfirmaproductionofCompanyBwith
        productofCompanyA."""

        product_a=self.env['product.product'].create({
            'name':'p1',
            'company_id':self.company_a.id,
        })
        mo=self.env['mrp.production'].create({
            'product_id':product_a.id,
            'product_uom_id':product_a.uom_id.id,
            'company_id':self.company_b.id,
        })
        withself.assertRaises(UserError):
            mo.action_confirm()

    deftest_production_2(self):
        """Checkthatconfirmingaproductionincompanybwithuser_awillcreate
        stockmovesoncompanyb."""

        product_a=self.env['product.product'].create({
            'name':'p1',
            'company_id':self.company_a.id,
        })
        component_a=self.env['product.product'].create({
            'name':'p2',
            'company_id':self.company_a.id,
        })
        self.env['mrp.bom'].create({
            'product_id':product_a.id,
            'product_tmpl_id':product_a.product_tmpl_id.id,
            'company_id':self.company_a.id,
            'bom_line_ids':[(0,0,{'product_id':component_a.id})]
        })
        mo_form=Form(self.env['mrp.production'].with_user(self.user_a))
        mo_form.product_id=product_a
        mo=mo_form.save()
        mo.with_user(self.user_b).action_confirm()
        self.assertEqual(mo.move_raw_ids.company_id,self.company_a)
        self.assertEqual(mo.move_finished_ids.company_id,self.company_a)

    deftest_product_produce_1(self):
        """Checkthatusingafinishedlotofcompanybintheproducewizardofaproduction
        ofcompanyaisnotallowed"""

        product=self.env['product.product'].create({
            'name':'p1',
            'tracking':'lot',
        })
        component=self.env['product.product'].create({
            'name':'p2',
        })
        lot_b=self.env['stock.production.lot'].create({
            'product_id':product.id,
            'company_id':self.company_b.id,
        })
        self.env['mrp.bom'].create({
            'product_id':product.id,
            'product_tmpl_id':product.product_tmpl_id.id,
            'company_id':self.company_a.id,
            'bom_line_ids':[(0,0,{'product_id':component.id})]
        })
        mo_form=Form(self.env['mrp.production'].with_user(self.user_a))
        mo_form.product_id=product
        mo_form.lot_producing_id=lot_b
        mo=mo_form.save()
        withself.assertRaises(UserError):
            mo.with_user(self.user_b).action_confirm()

    deftest_product_produce_2(self):
        """Checkthatusingacomponentlotofcompanybintheproducewizardofaproduction
        ofcompanyaisnotallowed"""

        product=self.env['product.product'].create({
            'name':'p1',
        })
        component=self.env['product.product'].create({
            'name':'p2',
            'tracking':'lot',
        })
        lot_b=self.env['stock.production.lot'].create({
            'product_id':component.id,
            'company_id':self.company_b.id,
        })
        self.env['mrp.bom'].create({
            'product_id':product.id,
            'product_tmpl_id':product.product_tmpl_id.id,
            'company_id':self.company_a.id,
            'bom_line_ids':[(0,0,{'product_id':component.id})]
        })
        mo_form=Form(self.env['mrp.production'].with_user(self.user_a))
        mo_form.product_id=product
        mo=mo_form.save()
        mo.with_user(self.user_b).action_confirm()
        mo_form=Form(mo)
        mo_form.qty_producing=1
        mo=mo_form.save()
        details_operation_form=Form(mo.move_raw_ids[0],view=self.env.ref('stock.view_stock_move_operations'))
        withdetails_operation_form.move_line_ids.edit(0)asml:
            ml.lot_id=lot_b
            ml.qty_done=1
        details_operation_form.save()
        withself.assertRaises(UserError):
            mo.button_mark_done()


    deftest_partner_1(self):
        """Onaproductwithoutcompany,asauserofCompanyB,checkitisnotpossibletousea
        locationlimitedtoCompanyAas`property_stock_production`"""

        shared_product=self.env['product.product'].create({
            'name':'SharedProduct',
            'company_id':False,
        })
        withself.assertRaises(UserError):
            shared_product.with_user(self.user_b).property_stock_production=self.stock_location_a
