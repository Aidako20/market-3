#-*-coding:utf-8-*-
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimporttagged
fromflectraimportfields


@tagged('post_install','-at_install')
classTestAccountDebitNote(AccountTestInvoicingCommon):

    deftest_00_debit_note_out_invoice(self):
        """DebitNoteofaregularCustomerInvoice"""
        invoice=self.init_invoice('out_invoice',products=self.product_a+self.product_b)
        invoice.action_post()
        move_debit_note_wiz=self.env['account.debit.note'].with_context(active_model="account.move",
                                                                       active_ids=invoice.ids).create({
            'date':fields.Date.from_string('2019-02-01'),
            'reason':'noreason',
            'copy_lines':True,
        })
        move_debit_note_wiz.create_debit()

        #Searchfortheoriginalinvoice
        debit_note=self.env['account.move'].search([('debit_origin_id','=',invoice.id)])
        debit_note.ensure_one()
        self.assertEqual(len(debit_note.invoice_line_ids),2,"Shouldhavecopiedtheinvoicelines")
        self.assertEqual(debit_note.move_type,'out_invoice','Typeofdebitnoteshouldbethesameastheoriginalinvoice')
        self.assertEqual(debit_note.state,'draft','Weshouldcreatedebitnotesindraftstate')

    deftest_10_debit_note_in_refund(self):
        """DebitNoteofavendorrefund(isaregularvendorbill)"""
        invoice=self.init_invoice('in_refund',products=self.product_a+self.product_b)
        invoice.action_post()
        move_debit_note_wiz=self.env['account.debit.note'].with_context(active_model="account.move",
                                                                          active_ids=invoice.ids).create({
            'date':fields.Date.from_string('2019-02-01'),
            'reason':'inordertocancelrefund',
        })
        move_debit_note_wiz.create_debit()

        #Searchfortheoriginalinvoice
        debit_note=self.env['account.move'].search([('debit_origin_id','=',invoice.id)])
        debit_note.ensure_one()

        self.assertFalse(debit_note.invoice_line_ids,'Weshouldnotcopylinesbydefaultondebitnotes')
        self.assertEqual(debit_note.move_type,'in_invoice','Typeofdebitnoteshouldnotberefundanymore')
        self.assertEqual(debit_note.state,'draft','Weshouldcreatedebitnotesindraftstate')
