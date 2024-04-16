#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importflectra.tests
fromflectra.addons.product_matrix.testsimportcommon


@flectra.tests.tagged('post_install','-at_install')
classTestSaleMatrixUi(common.TestMatrixCommon):

    """
        Thistestneedssale_managementmoduletowork.
    """

    deftest_sale_matrix_ui(self):
        #Setthetemplateasconfigurablebymatrix.
        self.matrix_template.product_add_mode="matrix"

        self.start_tour("/web",'sale_matrix_tour',login="admin")

        #Ensuressomedynamiccreatevariantshavebeencreatedbythematrix
        #EnsuresaSOhasbeencreatedwithexactlyxlines...

        self.assertEqual(len(self.matrix_template.product_variant_ids),8)
        self.assertEqual(len(self.matrix_template.product_variant_ids.product_template_attribute_value_ids),6)
        self.assertEqual(len(self.matrix_template.attribute_line_ids.product_template_value_ids),8)
        self.env['sale.order.line'].search([('product_id','in',self.matrix_template.product_variant_ids.ids)]).order_id.action_confirm()

        self.matrix_template.flush()
        self.assertEqual(round(self.matrix_template.sales_count,2),56.8)
        forvariantinself.matrix_template.product_variant_ids:
            #5and9.2becauseofnovariantattributes
            self.assertIn(round(variant.sales_count,2),[5,9.2])

        #EnsurenoduplicatelinehasbeencreatedontheSO.
        #NB:the*2isbecausetheno_variantattributedoesn'tcreateavariant
        #butstillgivesdifferentorderlines.
        self.assertEqual(
            len(self.env['sale.order.line'].search([('product_id','in',self.matrix_template.product_variant_ids.ids)])),
            len(self.matrix_template.product_variant_ids)*2
        )
