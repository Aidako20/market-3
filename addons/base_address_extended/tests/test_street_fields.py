#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels
fromflectra.tests.commonimportSavepointCase


classTestStreetFields(SavepointCase):

    @classmethod
    defsetUpClass(cls):
        super(TestStreetFields,cls).setUpClass()
        cls.Partner=cls.env['res.partner']
        cls.env.ref('base.be').write({'street_format':'%(street_name)s,%(street_number)s/%(street_number2)s'})
        cls.env.ref('base.us').write({'street_format':'%(street_number)s/%(street_number2)s%(street_name)s'})
        cls.env.ref('base.ch').write({'street_format':'header%(street_name)s,%(street_number)s-%(street_number2)strailer'})
        cls.env.ref('base.mx').write({'street_format':'%(street_name)s%(street_number)s/%(street_number2)s'})

    defassertStreetVals(self,record,street_data):
        forkey,valinstreet_data.items():
            ifkeynotin['street','street_name','street_number','street_number2','name','city','country_id']:
                continue
            ifisinstance(record[key],models.BaseModel):
                self.assertEqual(record[key].id,val,'Wronglyformattedstreetfield%s:expected%s,received%s'%(key,val,record[key]))
            else:
                self.assertEqual(record[key],val,'Wronglyformattedstreetfield%s:expected%s,received%s'%(key,val,record[key]))

    deftest_company_create(self):
        """Willtestthecomputeandinversemethodsofstreetfieldswhencreatingpartnerrecords."""
        us_id=self.env.ref('base.us').id
        mx_id=self.env.ref('base.mx').id
        ch_id=self.env.ref('base.ch').id
        input_values=[
            {'country_id':us_id,'street':'40/2bChausseedeNamur'},
            {'country_id':us_id,'street':'40ChausseedeNamur'},
            {'country_id':us_id,'street':'ChausseedeNamur'},
            {'country_id':mx_id,'street':'Av.MiguelHidalgoyCostilla601'},
            {'country_id':mx_id,'street':'Av.MiguelHidalgoyCostilla601/40'},
            {'country_id':ch_id,'street':'headerChausseedeNamur,40-2btrailer'},
            {'country_id':ch_id,'street':'headerChausseedeNamur,40trailer'},
            {'country_id':ch_id,'street':'headerChausseedeNamurtrailer'},
        ]
        expected=[
            {'street_name':'ChausseedeNamur','street_number':'40','street_number2':'2b'},
            {'street_name':'ChausseedeNamur','street_number':'40','street_number2':False},
            {'street_name':'deNamur','street_number':'Chaussee','street_number2':False},
            {'street_name':'Av.MiguelHidalgoyCostilla','street_number':'601','street_number2':False},
            {'street_name':'Av.MiguelHidalgoyCostilla','street_number':'601','street_number2':'40'},
            {'street_name':'ChausseedeNamur','street_number':'40','street_number2':'2b'},
            {'street_name':'ChausseedeNamur','street_number':'40','street_number2':False},
            {'street_name':'ChausseedeNamur','street_number':False,'street_number2':False}
        ]

        #teststreet->streetvalues(compute)
        foridx,(company_values,expected_vals)inenumerate(zip(input_values,expected)):
            company_values['name']='Test-%2d'%idx
            company=self.env['res.company'].create(company_values)
            self.assertStreetVals(company,expected_vals)
            self.assertStreetVals(company.partner_id,expected_vals)

        #teststreet_values->street(inverse)
        foridx,(company_values,expected_vals)inenumerate(zip(input_values,expected)):
            company_values['name']='TestNew-%2d'%idx
            expected_street=company_values.pop('street')
            company_values.update(expected_vals)
            company=self.env['res.company'].create(company_values)
            self.assertEqual(company.street,expected_street)
            self.assertStreetVals(company,company_values)
            self.assertEqual(company.partner_id.street,expected_street)
            self.assertStreetVals(company.partner_id,company_values)

    deftest_company_write(self):
        """Willtestthecomputeandinversemethodsofstreetfieldswhenupdatingpartnerrecords."""
        be_id=self.env.ref('base.be').id
        company=self.env['res.company'].create({
            'name':'Test',
            'country_id':be_id,
            'street':'ChausseedeNamur,40/2b'
        })
        self.assertStreetVals(company,{'street_name':'ChausseedeNamur','street_number':'40','street_number2':'2b'})

        input_values=[
            {'street':'ChausseedeNamur,43'},
            {'street':'ChausseedeNamur'},
            {'street_name':'CheedeNamur','street_number':'40'},
            {'street_number2':'4'},
            {'country_id':self.env.ref('base.us').id},
        ]
        expected=[
            {'street_name':'ChausseedeNamur','street_number':'43','street_number2':False},
            {'street_name':'ChausseedeNamur','street_number':False,'street_number2':False},
            {'street_name':'CheedeNamur','street_number':'40','street_number2':False,'street':'CheedeNamur,40'},
            {'street_name':'CheedeNamur','street_number':'40','street_number2':'4','street':'CheedeNamur,40/4'},
            {'street_name':'CheedeNamur','street_number':'40','street_number2':'4','street':'40/4CheedeNamur'},
        ]

        #testbothcomputeandinverse(couldprobablybepimp)
        forwrite_values,expected_valsinzip(input_values,expected):
            company.write(write_values)
            self.assertStreetVals(company,expected_vals)
            self.assertStreetVals(company.partner_id,expected_vals)

    deftest_partner_create(self):
        """Willtestthecomputeandinversemethodsofstreetfieldswhencreatingpartnerrecords."""
        us_id=self.env.ref('base.us').id
        mx_id=self.env.ref('base.mx').id
        ch_id=self.env.ref('base.ch').id
        input_values=[
            {'country_id':us_id,'street':'40/2bChausseedeNamur'},
            {'country_id':us_id,'street':'40ChausseedeNamur'},
            {'country_id':us_id,'street':'ChausseedeNamur'},
            {'country_id':mx_id,'street':'Av.MiguelHidalgoyCostilla601'},
            {'country_id':mx_id,'street':'Av.MiguelHidalgoyCostilla601/40'},
            {'country_id':ch_id,'street':'headerChausseedeNamur,40-2btrailer'},
            {'country_id':ch_id,'street':'headerChausseedeNamur,40trailer'},
            {'country_id':ch_id,'street':'headerChausseedeNamurtrailer'},
        ]
        expected=[
            {'street_name':'ChausseedeNamur','street_number':'40','street_number2':'2b'},
            {'street_name':'ChausseedeNamur','street_number':'40','street_number2':False},
            {'street_name':'deNamur','street_number':'Chaussee','street_number2':False},
            {'street_name':'Av.MiguelHidalgoyCostilla','street_number':'601','street_number2':False},
            {'street_name':'Av.MiguelHidalgoyCostilla','street_number':'601','street_number2':'40'},
            {'street_name':'ChausseedeNamur','street_number':'40','street_number2':'2b'},
            {'street_name':'ChausseedeNamur','street_number':'40','street_number2':False},
            {'street_name':'ChausseedeNamur','street_number':False,'street_number2':False}
        ]

        #teststreet->streetvalues(compute)
        forpartner_values,expected_valsinzip(input_values,expected):
            partner_values['name']='Test'
            partner=self.env['res.partner'].create(partner_values)
            self.assertStreetVals(partner,expected_vals)

        #teststreet_values->street(inverse)
        forpartner_values,expected_valsinzip(input_values,expected):
            partner_values['name']='Test'
            expected_street=partner_values.pop('street')
            partner_values.update(expected_vals)
            partner=self.env['res.partner'].create(partner_values)
            self.assertEqual(partner.street,expected_street)
            self.assertStreetVals(partner,partner_values)

    deftest_partner_write(self):
        """Willtestthecomputeandinversemethodsofstreetfieldswhenupdatingpartnerrecords."""
        be_id=self.env.ref('base.be').id
        partner=self.env['res.partner'].create({
            'name':'Test',
            'country_id':be_id,
            'street':'ChausseedeNamur,40/2b'
        })
        self.assertStreetVals(partner,{'street_name':'ChausseedeNamur','street_number':'40','street_number2':'2b'})

        input_values=[
            {'street':'ChausseedeNamur,43'},
            {'street':'ChausseedeNamur'},
            {'street_name':'CheedeNamur','street_number':'40'},
            {'street_number2':'4'},
            {'country_id':self.env.ref('base.us').id},
        ]
        expected=[
            {'street_name':'ChausseedeNamur','street_number':'43','street_number2':False},
            {'street_name':'ChausseedeNamur','street_number':False,'street_number2':False},
            {'street_name':'CheedeNamur','street_number':'40','street_number2':False,'street':'CheedeNamur,40'},
            {'street_name':'CheedeNamur','street_number':'40','street_number2':'4','street':'CheedeNamur,40/4'},
            {'street_name':'CheedeNamur','street_number':'40','street_number2':'4','street':'40/4CheedeNamur'},
        ]

        #testbothcomputeandinverse(couldprobablybepimp)
        forwrite_values,expected_valsinzip(input_values,expected):
            partner.write(write_values)
            self.assertStreetVals(partner,expected_vals)
