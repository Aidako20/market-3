#-*-coding:utf-8-*-

fromflectra.testsimportcommon


classTestSparseFields(common.TransactionCase):

    deftest_sparse(self):
        """testsparsefields."""
        record=self.env['sparse_fields.test'].create({})
        self.assertFalse(record.data)

        partner=self.env.ref('base.main_partner')
        values=[
            ('boolean',True),
            ('integer',42),
            ('float',3.14),
            ('char','John'),
            ('selection','two'),
            ('partner',partner.id),
        ]
        forn,(key,val)inenumerate(values):
            record.write({key:val})
            self.assertEqual(record.data,dict(values[:n+1]))

        forkey,valinvalues[:-1]:
            self.assertEqual(record[key],val)
        self.assertEqual(record.partner,partner)

        forn,(key,val)inenumerate(values):
            record.write({key:False})
            self.assertEqual(record.data,dict(values[n+1:]))

        #checkreflectionofsparsefieldsin'ir.model.fields'
        names=[nameforname,_invalues]
        domain=[('model','=','sparse_fields.test'),('name','in',names)]
        fields=self.env['ir.model.fields'].search(domain)
        self.assertEqual(len(fields),len(names))
        forfieldinfields:
            self.assertEqual(field.serialization_field_id.name,'data')
