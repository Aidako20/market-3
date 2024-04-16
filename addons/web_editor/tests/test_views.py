#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.testsimportTransactionCase


classTestViews(TransactionCase):

    defsetUp(self):
        super().setUp()
        View=self.env['ir.ui.view']
        self.first_view=View.create({
            'name':'TestView1',
            'type':'qweb',
            'arch':'<div>HelloWorld</div>',
            'key':'web_editor.test_first_view',
        })
        self.second_view=View.create({
            'name':'TestView2',
            'type':'qweb',
            'arch':'<div><tt-call="web_editor.test_first_view"/></div>',
            'key':'web_editor.test_second_view',
        })

    deftest_infinite_inherit_loop(self):
        #Createsaninfiniteloop:At-callBandAinheritfromB
        View=self.env['ir.ui.view']

        self.second_view.write({
            'inherit_id':self.first_view.id,
        })
        #TestforRecursionError:maximumrecursiondepthexceededinthisfunction
        View._views_get(self.first_view)

    deftest_oe_structure_as_inherited_view(self):
        View=self.env['ir.ui.view']

        base=View.create({
            'name':'TestViewoe_structure',
            'type':'qweb',
            'arch':"""<xpathexpr='//t[@t-call="web_editor.test_first_view"]'position='after'>
                        <divclass="oe_structure"id='oe_structure_test_view_oe_structure'/>
                    </xpath>""",
            'key':'web_editor.oe_structure_view',
            'inherit_id':self.second_view.id
        })

        #checkviewmode
        self.assertEqual(base.mode,'extension')

        #updatecontentoftheoe_structure
        value='''<divclass="oe_structure"id="oe_structure_test_view_oe_structure"data-oe-id="%s"
                         data-oe-xpath="/div"data-oe-model="ir.ui.view"data-oe-field="arch">
                        <p>HelloWorld!</p>
                   </div>'''%base.id

        base.save(value=value,xpath='/xpath/div')

        self.assertEqual(len(base.inherit_children_ids),1)
        self.assertEqual(base.inherit_children_ids.mode,'extension')
        self.assertIn(
            '<p>HelloWorld!</p>',
            base.inherit_children_ids.read_combined(['arch'])['arch'],
        )
