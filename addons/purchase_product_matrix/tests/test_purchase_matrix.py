#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importflectra.tests
fromflectra.addons.product_matrix.tests.commonimportTestMatrixCommon


@flectra.tests.tagged('post_install','-at_install')
classTestPurchaseMatrixUi(TestMatrixCommon):

    deftest_purchase_matrix_ui(self):
        self.start_tour("/web",'purchase_matrix_tour',login="admin")

        #Ensuressomedynamiccreatevariantshavebeencreatedbythematrix
        #EnsuresaPOhasbeencreatedwithexactlyxlines...

        self.assertEqual(len(self.matrix_template.product_variant_ids),8)
        self.assertEqual(len(self.matrix_template.product_variant_ids.product_template_attribute_value_ids),6)
        self.assertEqual(len(self.matrix_template.attribute_line_ids.product_template_value_ids),8)
        self.env['purchase.order.line'].search([('product_id','in',self.matrix_template.product_variant_ids.ids)]).order_id.button_confirm()

        self.matrix_template.flush()
        self.assertEqual(round(self.matrix_template.purchased_product_qty,2),56.8)
        forvariantinself.matrix_template.product_variant_ids:
            #5and9.2becauseofnovariantattributes
            self.assertIn(round(variant.purchased_product_qty,2),[5,9.2])

        #EnsurenoduplicatelinehasbeencreatedonthePO.
        #NB:the*2isbecausetheno_variantattributedoesn'tcreateavariant
        #butstillgivesdifferentorderlines.
        self.assertEqual(
            len(self.env['purchase.order.line'].search([('product_id','in',self.matrix_template.product_variant_ids.ids)])),
            len(self.matrix_template.product_variant_ids)*2
        )
