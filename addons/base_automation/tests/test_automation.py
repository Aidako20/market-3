#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.testsimportTransactionCase
fromflectra.exceptionsimportUserError

importflectra.tests

@flectra.tests.tagged('post_install','-at_install')
classTestAutomation(TransactionCase):

    deftest_01_on_create(self):
        """Simpleon_createwithadminuser"""
        self.env["base.automation"].create({
            "name":"ForceArchivedContacts",
            "trigger":"on_create_or_write",
            "model_id":self.env.ref("base.model_res_partner").id,
            "type":"ir.actions.server",
            "trigger_field_ids":[(6,0,[self.env.ref("base.field_res_partner__name").id])],
            "fields_lines":[(0,0,{
                "col1":self.env.ref("base.field_res_partner__active").id,
                "evaluation_type":"equation",
                "value":"False",
            })],
        })

        #verifythepartnercanbecreatedandtheactionstillruns
        bilbo=self.env["res.partner"].create({"name":"BilboBaggins"})
        self.assertFalse(bilbo.active)

        #verifythepartnercanbeupdatedandtheactionstillruns
        bilbo.active=True
        bilbo.name="Bilbo"
        self.assertFalse(bilbo.active)


    deftest_02_on_create_restricted(self):
        """on_createactionwithlowportaluser"""
        action=self.env["base.automation"].create({
            "name":"ForceArchivedFilters",
            "trigger":"on_create_or_write",
            "model_id":self.env.ref("base.model_ir_filters").id,
            "type":"ir.actions.server",
            "trigger_field_ids":[(6,0,[self.env.ref("base.field_ir_filters__name").id])],
            "fields_lines":[(0,0,{
                "col1":self.env.ref("base.field_ir_filters__active").id,
                "evaluation_type":"equation",
                "value":"False",
            })],
        })
        #actioncachedwascachedwithadmin,forceCacheMiss
        action.env.clear()

        self_portal=self.env["ir.filters"].with_user(self.env.ref("base.user_demo").id)
        #verifytheportalusercancreateir.filtersbutcannotreadbase.automation
        self.assertTrue(self_portal.env["ir.filters"].check_access_rights("create",raise_exception=False))
        self.assertFalse(self_portal.env["base.automation"].check_access_rights("read",raise_exception=False))

        #verifythefiltercanbecreatedandtheactionstillruns
        filters=self_portal.create({
            "name":"WhereisBilbo?",
            "domain":"[('name','ilike','bilbo')]",
            "model_id":"res.partner",
        })
        self.assertFalse(filters.active)

        #verifythefiltercanbeupdatedandtheactionstillruns
        filters.active=True
        filters.name="WhereisBilboBaggins?"
        self.assertFalse(filters.active)


    deftest_03_on_change_restricted(self):
        """on_createactionwithlowportaluser"""
        action=self.env["base.automation"].create({
            "name":"ForceArchivedFilters",
            "trigger":"on_change",
            "model_id":self.env.ref("base.model_ir_filters").id,
            "type":"ir.actions.server",
            "on_change_field_ids":[(6,0,[self.env.ref("base.field_ir_filters__name").id])],
            "state":"code",
            "code":"""action={'value':{'active':False}}""",
        })
        #actioncachedwascachedwithadmin,forceCacheMiss
        action.env.clear()

        self_portal=self.env["ir.filters"].with_user(self.env.ref("base.user_demo").id)

        #simulateaonchangecallonname
        onchange=self_portal.onchange({},[],{"name":"1","active":""})
        self.assertEqual(onchange["value"]["active"],False)
