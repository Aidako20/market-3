#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimporttagged,Form
fromflectraimportfields


fromdatetimeimporttimedelta,datetime
fromfreezegunimportfreeze_time


@tagged('-at_install','post_install')
classTestPurchase(AccountTestInvoicingCommon):

    deftest_date_planned(self):
        """Setadateplannedon2POlines.CheckthatthePOdate_plannedistheearliestPOlinedate
        planned.Changeoneofthedatessoitisevenearlierandcheckthatthedate_plannedissetto
        thisearlierdate.
        """
        po=Form(self.env['purchase.order'])
        po.partner_id=self.partner_a
        withpo.order_line.new()aspo_line:
            po_line.product_id=self.product_a
            po_line.product_qty=1
            po_line.price_unit=100
        withpo.order_line.new()aspo_line:
            po_line.product_id=self.product_b
            po_line.product_qty=10
            po_line.price_unit=200
        po=po.save()

        #CheckthatthesamedateisplannedonbothPOlines.
        self.assertNotEqual(po.order_line[0].date_planned,False)
        self.assertAlmostEqual(po.order_line[0].date_planned,po.order_line[1].date_planned,delta=timedelta(seconds=10))
        self.assertAlmostEqual(po.order_line[0].date_planned,po.date_planned,delta=timedelta(seconds=10))

        orig_date_planned=po.order_line[0].date_planned

        #SetanearlierdateplannedonaPOlineandcheckthatthePOexpecteddatematchesit.
        new_date_planned=orig_date_planned-timedelta(hours=1)
        po.order_line[0].date_planned=new_date_planned
        self.assertAlmostEqual(po.order_line[0].date_planned,po.date_planned,delta=timedelta(seconds=10))

        #SetanevenearlierdateplannedontheotherPOlineandcheckthatthePOexpecteddatematchesit.
        new_date_planned=orig_date_planned-timedelta(hours=72)
        po.order_line[1].date_planned=new_date_planned
        self.assertAlmostEqual(po.order_line[1].date_planned,po.date_planned,delta=timedelta(seconds=10))

    @freeze_time("2021-12-0221:00")
    deftest_date_planned_02(self):
        """ChecktheplanneddatedefinitionwhenserverisUTCanduserisUTC+11"""
        #UTC: 2021-12-0221:00
        #User:2021-12-0308:00(UTC+11)
        self.env.user.tz="Australia/Sydney"
        po_form=Form(self.env['purchase.order'])
        po_form.partner_id=self.partner_a
        withpo_form.order_line.new()aspo_line:
            po_line.product_id=self.product_a
        self.assertEqual(po_form.date_planned,datetime.fromisoformat("2021-12-0301:00:00"),
                         "Shouldbe2021-12-0301:00:00,i.e.2021-12-0312:00:00UTC+11")

    deftest_purchase_order_sequence(self):
        PurchaseOrder=self.env['purchase.order'].with_context(tracking_disable=True)
        company=self.env.user.company_id
        self.env['ir.sequence'].search([
            ('code','=','purchase.order'),
        ]).write({
            'use_date_range':True,'prefix':'PO/%(range_year)s/',
        })
        vals={
            'partner_id':self.partner_a.id,
            'company_id':company.id,
            'currency_id':company.currency_id.id,
            'date_order':'2019-01-01',
        }
        purchase_order=PurchaseOrder.create(vals.copy())
        self.assertTrue(purchase_order.name.startswith('PO/2019/'))
        vals['date_order']='2020-01-01'
        purchase_order=PurchaseOrder.create(vals.copy())
        self.assertTrue(purchase_order.name.startswith('PO/2020/'))
        #InEU/BXLtz,thisisactuallyalready01/01/2020
        vals['date_order']='2019-12-3123:30:00'
        purchase_order=PurchaseOrder.with_context(tz='Europe/Brussels').create(vals.copy())
        self.assertTrue(purchase_order.name.startswith('PO/2020/'))

    deftest_reminder_1(self):
        """Settosendremindertoday,checkifaremindercanbesendtothe
        partner.
        """
        po=Form(self.env['purchase.order'])
        po.partner_id=self.partner_a
        withpo.order_line.new()aspo_line:
            po_line.product_id=self.product_a
            po_line.product_qty=1
            po_line.price_unit=100
        withpo.order_line.new()aspo_line:
            po_line.product_id=self.product_b
            po_line.product_qty=10
            po_line.price_unit=200
        #settosendremindertoday
        po.date_planned=fields.Datetime.now()+timedelta(days=1)
        po.receipt_reminder_email=True
        po.reminder_date_before_receipt=1
        po=po.save()
        po.button_confirm()

        #checkvendorisamessagerecipient
        self.assertTrue(po.partner_idinpo.message_partner_ids)

        old_messages=po.message_ids
        po._send_reminder_mail()
        messages_send=po.message_ids-old_messages
        #checkremindersend
        self.assertTrue(messages_send)
        self.assertTrue(po.partner_idinmessages_send.mapped('partner_ids'))

        #checkconfirmbutton
        po.confirm_reminder_mail()
        self.assertTrue(po.mail_reminder_confirmed)

    deftest_reminder_2(self):
        """Settosendremindertomorrow,checkifnoremindercanbesend.
        """
        po=Form(self.env['purchase.order'])
        po.partner_id=self.partner_a
        withpo.order_line.new()aspo_line:
            po_line.product_id=self.product_a
            po_line.product_qty=1
            po_line.price_unit=100
        withpo.order_line.new()aspo_line:
            po_line.product_id=self.product_b
            po_line.product_qty=10
            po_line.price_unit=200
        #settosendremindertomorrow
        po.date_planned=fields.Datetime.now()+timedelta(days=2)
        po.receipt_reminder_email=True
        po.reminder_date_before_receipt=1
        po=po.save()
        po.button_confirm()

        #checkvendorisamessagerecipient
        self.assertTrue(po.partner_idinpo.message_partner_ids)

        old_messages=po.message_ids
        po._send_reminder_mail()
        messages_send=po.message_ids-old_messages
        #checknoremindersend
        self.assertFalse(messages_send)

    deftest_update_date_planned(self):
        po=Form(self.env['purchase.order'])
        po.partner_id=self.partner_a
        withpo.order_line.new()aspo_line:
            po_line.product_id=self.product_a
            po_line.product_qty=1
            po_line.price_unit=100
            po_line.date_planned='2020-06-0600:00:00'
        withpo.order_line.new()aspo_line:
            po_line.product_id=self.product_b
            po_line.product_qty=10
            po_line.price_unit=200
            po_line.date_planned='2020-06-0600:00:00'
        po=po.save()
        po.button_confirm()

        #updatefirstline
        po._update_date_planned_for_lines([(po.order_line[0],fields.Datetime.today())])
        self.assertEqual(po.order_line[0].date_planned,fields.Datetime.today())
        activity=self.env['mail.activity'].search([
            ('summary','=','DateUpdated'),
            ('res_model_id','=','purchase.order'),
            ('res_id','=',po.id),
        ])
        self.assertTrue(activity)
        self.assertIn(
            '<p>partner_amodifiedreceiptdatesforthefollowingproducts:</p><p>\xa0-product_afrom2020-06-06to%s</p>'%fields.Date.today(),
            activity.note,
        )

        #updatesecondline
        po._update_date_planned_for_lines([(po.order_line[1],fields.Datetime.today())])
        self.assertEqual(po.order_line[1].date_planned,fields.Datetime.today())
        self.assertIn(
            '<p>partner_amodifiedreceiptdatesforthefollowingproducts:</p><p>\xa0-product_afrom2020-06-06to%s</p><p>\xa0-product_bfrom2020-06-06to%s</p>'%(fields.Date.today(),fields.Date.today()),
            activity.note,
        )

    deftest_with_different_uom(self):
        """Thistestensuresthattheunitpriceiscorrectlycomputed"""
        uom_units=self.env['ir.model.data'].xmlid_to_object('uom.product_uom_unit')
        uom_dozens=self.env['ir.model.data'].xmlid_to_object('uom.product_uom_dozen')
        uom_pairs=self.env['uom.uom'].create({
            'name':'Pairs',
            'category_id':uom_units.category_id.id,
            'uom_type':'bigger',
            'factor_inv':2,
            'rounding':1,
        })
        product_data={
            'name':'SuperProduct',
            'type':'consu',
            'uom_id':uom_units.id,
            'uom_po_id':uom_pairs.id,
            'standard_price':100
        }
        product_01=self.env['product.product'].create(product_data)
        product_02=self.env['product.product'].create(product_data)

        po_form=Form(self.env['purchase.order'])
        po_form.partner_id=self.partner_a
        withpo_form.order_line.new()aspo_line:
            po_line.product_id=product_01
        withpo_form.order_line.new()aspo_line:
            po_line.product_id=product_02
            po_line.product_uom=uom_dozens
        po=po_form.save()

        self.assertEqual(po.order_line[0].price_unit,200)
        self.assertEqual(po.order_line[1].price_unit,1200)

    deftest_on_change_quantity_description(self):
        """
        Whenauserchangesthequantityofaproductinapurchaseorderit
        shouldnotchangethedescriptionifthedescritpionwaschangedby
        theuserbefore
        """
        self.env.user.write({'company_id':self.company_data['company'].id})

        po=Form(self.env['purchase.order'])
        po.partner_id=self.partner_a
        withpo.order_line.new()aspol:
            pol.product_id=self.product_a
            pol.product_qty=1

        pol.name="Newcustomdescription"
        pol.product_qty+=1
        self.assertEqual(pol.name,"Newcustomdescription")
