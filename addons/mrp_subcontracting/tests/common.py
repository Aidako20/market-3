#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.tests.commonimportForm,SavepointCase

classTestMrpSubcontractingCommon(SavepointCase):

    @classmethod
    defsetUpClass(cls):
        super(TestMrpSubcontractingCommon,cls).setUpClass()
        #1:Createasubcontractingpartner
        main_partner=cls.env['res.partner'].create({'name':'main_partner'})
        cls.subcontractor_partner1=cls.env['res.partner'].create({
            'name':'subcontractor_partner',
            'parent_id':main_partner.id,
            'company_id':cls.env.ref('base.main_company').id,
        })

        #2.CreateaBOMofsubcontractingtype
        cls.comp1=cls.env['product.product'].create({
            'name':'Component1',
            'type':'product',
            'categ_id':cls.env.ref('product.product_category_all').id,
        })
        cls.comp2=cls.env['product.product'].create({
            'name':'Component2',
            'type':'product',
            'categ_id':cls.env.ref('product.product_category_all').id,
        })
        cls.finished=cls.env['product.product'].create({
            'name':'finished',
            'type':'product',
            'categ_id':cls.env.ref('product.product_category_all').id,
        })
        bom_form=Form(cls.env['mrp.bom'])
        bom_form.type='subcontract'
        bom_form.product_tmpl_id=cls.finished.product_tmpl_id
        bom_form.subcontractor_ids.add(cls.subcontractor_partner1)
        withbom_form.bom_line_ids.new()asbom_line:
            bom_line.product_id=cls.comp1
            bom_line.product_qty=1
        withbom_form.bom_line_ids.new()asbom_line:
            bom_line.product_id=cls.comp2
            bom_line.product_qty=1
        cls.bom=bom_form.save()

        #CreateaBoMforcls.comp2
        cls.comp2comp=cls.env['product.product'].create({
            'name':'componentforComponent2',
            'type':'product',
            'categ_id':cls.env.ref('product.product_category_all').id,
        })
        bom_form=Form(cls.env['mrp.bom'])
        bom_form.product_tmpl_id=cls.comp2.product_tmpl_id
        withbom_form.bom_line_ids.new()asbom_line:
            bom_line.product_id=cls.comp2comp
            bom_line.product_qty=1
        cls.comp2_bom=bom_form.save()

        cls.warehouse=cls.env['stock.warehouse'].search([],limit=1)
