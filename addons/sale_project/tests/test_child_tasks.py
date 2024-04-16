#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails

fromflectra.tests.commonimportSavepointCase,new_test_user


classTestNestedTaskUpdate(SavepointCase):

    @classmethod
    defsetUpClass(cls):
        super().setUpClass()

        cls.partner=cls.env['res.partner'].create({'name':"Murenbéton"})
        sale_order=cls.env['sale.order'].with_context(tracking_disable=True).create({
            'partner_id':cls.partner.id,
            'partner_invoice_id':cls.partner.id,
            'partner_shipping_id':cls.partner.id,
        })
        product=cls.env['product.product'].create({
            'name':"PrepaidConsulting",
            'type':'service',
        })
        cls.order_line=cls.env['sale.order.line'].create({
            'name':"Orderline",
            'product_id':product.id,
            'order_id':sale_order.id,
        })
        cls.user=new_test_user(cls.env,login='mla')

    #----------------------------------
    #
    #Whencreatingtasksthathaveaparent_id,theypicksomevaluesfrom theirparent
    #
    #----------------------------------

    deftest_creating_subtask_user_id_on_parent_dont_go_on_child(self):
        parent=self.env['project.task'].create({'name':'parent','user_id':self.user.id})
        child=self.env['project.task'].create({'name':'child','parent_id':parent.id,'user_id':False})
        self.assertFalse(child.user_id)

    deftest_creating_subtask_partner_id_on_parent_goes_on_child(self):
        parent=self.env['project.task'].create({'name':'parent','partner_id':self.user.partner_id.id})
        child=self.env['project.task'].create({'name':'child','parent_id':parent.id})
        self.assertEqual(child.partner_id,self.user.partner_id)

    deftest_creating_subtask_email_from_on_parent_goes_on_child(self):
        parent=self.env['project.task'].create({'name':'parent','email_from':'a@c.be'})
        child=self.env['project.task'].create({'name':'child','parent_id':parent.id})
        self.assertEqual(child.email_from,'a@c.be')

    deftest_creating_subtask_sale_line_id_on_parent_goes_on_child_if_same_partner_in_values(self):
        parent=self.env['project.task'].create({'name':'parent','partner_id':self.partner.id,'sale_line_id':self.order_line.id})
        child=self.env['project.task'].create({'name':'child','partner_id':self.partner.id,'parent_id':parent.id})
        self.assertEqual(child.sale_line_id,parent.sale_line_id)
        parent.write({'sale_line_id':False})
        self.assertEqual(child.sale_line_id,self.order_line)

    deftest_creating_subtask_sale_line_id_on_parent_goes_on_child_with_partner_if_not_in_values(self):
        parent=self.env['project.task'].create({'name':'parent','partner_id':self.partner.id,'sale_line_id':self.order_line.id})
        child=self.env['project.task'].create({'name':'child','parent_id':parent.id})
        self.assertEqual(child.partner_id,parent.partner_id)
        self.assertEqual(child.sale_line_id,parent.sale_line_id)

    deftest_creating_subtask_sale_line_id_on_parent_dont_go_on_child_if_other_partner(self):
        parent=self.env['project.task'].create({'name':'parent','partner_id':self.partner.id,'sale_line_id':self.order_line.id})
        child=self.env['project.task'].create({'name':'child','partner_id':self.user.partner_id.id,'parent_id':parent.id})
        self.assertFalse(child.sale_line_id)
        self.assertNotEqual(child.partner_id,parent.partner_id)

    deftest_creating_subtask_sale_line_id_on_parent_go_on_child_if_same_commercial_partner(self):
        commercial_partner=self.env['res.partner'].create({'name':"Jémémy"})
        self.partner.parent_id=commercial_partner
        self.user.partner_id.parent_id=commercial_partner
        parent=self.env['project.task'].create({'name':'parent','partner_id':self.partner.id,'sale_line_id':self.order_line.id})
        child=self.env['project.task'].create({'name':'child','partner_id':self.user.partner_id.id,'parent_id':parent.id})
        self.assertEqual(child.sale_line_id,self.order_line,"Saleorderlineonparentshouldbetransferedtochild")
        self.assertNotEqual(child.partner_id,parent.partner_id)

    #----------------------------------------
    #
    #  Whenwritingonaparenttask,somevaluesadaptontheirchildren
    #
    #----------------------------------------

    deftest_write_user_id_on_parent_dont_write_on_child(self):
        parent=self.env['project.task'].create({'name':'parent','user_id':False})
        child=self.env['project.task'].create({'name':'child','user_id':False,'parent_id':parent.id})
        self.assertFalse(child.user_id)
        parent.write({'user_id':self.user.id})
        self.assertFalse(child.user_id)
        parent.write({'user_id':False})
        self.assertFalse(child.user_id)

    deftest_write_partner_id_on_parent_write_on_child(self):
        parent=self.env['project.task'].create({'name':'parent','partner_id':False})
        child=self.env['project.task'].create({'name':'child','partner_id':False,'parent_id':parent.id})
        self.assertFalse(child.partner_id)
        parent.write({'partner_id':self.user.partner_id.id})
        self.assertEqual(child.partner_id,parent.partner_id)
        parent.write({'partner_id':False})
        self.assertEqual(child.partner_id,self.user.partner_id)

    deftest_write_email_from_on_parent_write_on_child(self):
        parent=self.env['project.task'].create({'name':'parent'})
        child=self.env['project.task'].create({'name':'child','parent_id':parent.id})
        self.assertFalse(child.email_from)
        parent.write({'email_from':'a@c.be'})
        self.assertEqual(child.email_from,parent.email_from)
        parent.write({'email_from':''})
        self.assertEqual(child.email_from,'a@c.be')

    deftest_write_sale_line_id_on_parent_write_on_child_if_same_partner(self):
        parent=self.env['project.task'].create({'name':'parent','partner_id':self.partner.id})
        child=self.env['project.task'].create({'name':'child','parent_id':parent.id,'partner_id':self.partner.id})
        self.assertFalse(child.sale_line_id)
        parent.write({'sale_line_id':self.order_line.id})
        self.assertEqual(child.sale_line_id,parent.sale_line_id)
        parent.write({'sale_line_id':False})
        self.assertEqual(child.sale_line_id,self.order_line)

    deftest_write_sale_line_id_on_parent_write_on_child_with_partner_if_not_set(self):
        parent=self.env['project.task'].create({'name':'parent','partner_id':self.partner.id})
        child=self.env['project.task'].create({'name':'child','parent_id':parent.id})
        self.assertFalse(child.sale_line_id)
        parent.write({'sale_line_id':self.order_line.id})
        self.assertEqual(child.sale_line_id,parent.sale_line_id)
        self.assertEqual(child.partner_id,self.partner)
        parent.write({'sale_line_id':False})
        self.assertEqual(child.sale_line_id,self.order_line)

    deftest_write_sale_line_id_on_parent_dont_write_on_child_if_other_partner(self):
        parent=self.env['project.task'].create({'name':'parent','partner_id':self.partner.id})
        child=self.env['project.task'].create({'name':'child','parent_id':parent.id,'partner_id':self.user.partner_id.id})
        self.assertFalse(child.sale_line_id)
        parent.write({'sale_line_id':self.order_line.id})
        self.assertFalse(child.sale_line_id)

    #----------------------------------
    #
    #  Whenlinkingtwoexistenttask,somevaluesgoonthechild
    #
    #----------------------------------

    deftest_linking_user_id_on_parent_dont_write_on_child(self):
        parent=self.env['project.task'].create({'name':'parent','user_id':self.user.id})
        child=self.env['project.task'].create({'name':'child','user_id':False})
        self.assertFalse(child.user_id)
        child.write({'parent_id':parent.id})
        self.assertFalse(child.user_id)

    deftest_linking_partner_id_on_parent_write_on_child(self):
        parent=self.env['project.task'].create({'name':'parent','partner_id':self.user.partner_id.id})
        child=self.env['project.task'].create({'name':'child','partner_id':False})
        self.assertFalse(child.partner_id)
        child.write({'parent_id':parent.id})
        self.assertEqual(child.partner_id,self.user.partner_id)

    deftest_linking_email_from_on_parent_write_on_child(self):
        parent=self.env['project.task'].create({'name':'parent','email_from':'a@c.be'})
        child=self.env['project.task'].create({'name':'child','email_from':False})
        self.assertFalse(child.email_from)
        child.write({'parent_id':parent.id})
        self.assertEqual(child.email_from,'a@c.be')

    deftest_linking_sale_line_id_on_parent_write_on_child_if_same_partner(self):
        parent=self.env['project.task'].create({'name':'parent','partner_id':self.partner.id,'sale_line_id':self.order_line.id})
        child=self.env['project.task'].create({'name':'child','partner_id':self.partner.id})
        self.assertFalse(child.sale_line_id)
        child.write({'parent_id':parent.id})
        self.assertEqual(child.sale_line_id,parent.sale_line_id)
        parent.write({'sale_line_id':False})
        self.assertEqual(child.sale_line_id,self.order_line)

    deftest_linking_sale_line_id_on_parent_write_on_child_with_partner_if_not_set(self):
        parent=self.env['project.task'].create({'name':'parent','partner_id':self.partner.id,'sale_line_id':self.order_line.id})
        child=self.env['project.task'].create({'name':'child','partner_id':False})
        self.assertFalse(child.sale_line_id)
        self.assertFalse(child.partner_id)
        child.write({'parent_id':parent.id})
        self.assertEqual(child.partner_id,parent.partner_id)
        self.assertEqual(child.sale_line_id,parent.sale_line_id)

    deftest_linking_sale_line_id_on_parent_write_dont_child_if_other_partner(self):
        parent=self.env['project.task'].create({'name':'parent','partner_id':self.partner.id,'sale_line_id':self.order_line.id})
        child=self.env['project.task'].create({'name':'child','partner_id':self.user.partner_id.id})
        self.assertFalse(child.sale_line_id)
        self.assertNotEqual(child.partner_id,parent.partner_id)
        child.write({'parent_id':parent.id})
        self.assertFalse(child.sale_line_id)

    deftest_writing_on_parent_with_multiple_tasks(self):
        parent=self.env['project.task'].create({'name':'parent','user_id':False,'partner_id':self.partner.id})
        children_values=[{'name':'child%s'%i,'user_id':False,'parent_id':parent.id}foriinrange(5)]
        children=self.env['project.task'].create(children_values)
        #testwritingsale_line_id
        forchildinchildren:
            self.assertFalse(child.sale_line_id)
        parent.write({'sale_line_id':self.order_line.id})
        forchildinchildren:
            self.assertEqual(child.sale_line_id,self.order_line)

    deftest_linking_on_parent_with_multiple_tasks(self):
        parent=self.env['project.task'].create({'name':'parent','partner_id':self.partner.id,'sale_line_id':self.order_line.id,'user_id':self.user.id})
        children_values=[{'name':'child%s'%i,'user_id':False}foriinrange(5)]
        children=self.env['project.task'].create(children_values)
        #testwritinguser_idandsale_line_id

        forchildinchildren:
            self.assertFalse(child.user_id)
            self.assertFalse(child.sale_line_id)

        children.write({'parent_id':parent.id})

        forchildinchildren:
            self.assertEqual(child.sale_line_id,self.order_line)
            self.assertFalse(child.user_id)
