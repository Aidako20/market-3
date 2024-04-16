#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson
fromdatetimeimportdate
fromunittest.mockimportpatch

fromflectraimporthttp
fromflectra.testsimportcommon,tagged
fromflectra.tools.miscimportget_lang
fromflectra.addons.web.controllers.mainimportExportXlsxWriter
fromflectra.addons.mail.tests.commonimportmail_new_test_user


classXlsxCreatorCase(common.HttpCase):
    model_name=False

    def__init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.model=None

    defsetUp(self):
        super().setUp()
        self.model=self.env[self.model_name]

        mail_new_test_user(self.env,login='fof',password='123456789',groups='base.group_user,base.group_allow_export')
        self.session=self.authenticate('fof','123456789')

        self.worksheet={} #mockworksheet

        self.default_params={
            'domain':[],
            'fields':[{'name':field.name,'label':field.string}forfieldinself.model._fields.values()],
            'groupby':[],
            'ids':False,
            'import_compat':False,
            'model':self.model._name,
        }

    def_mock_write(self,row,column,value,style=None):
        ifisinstance(value,float):
            decimal_places=style.num_format[::-1].find('.')
            style_format="{:."+str(decimal_places)+"f}"
            self.worksheet[row,column]=style_format.format(value)
        else:
            self.worksheet[row,column]=str(value)

    defmake(self,values,context=None):
        returnself.model.with_context(**(contextor{})).create(values)

    defexport(self,values,fields=[],params={},context=None):
        self.worksheet={}
        self.make(values,context=context)

        iffieldsand'fields'notinparams:
            params['fields']=[{
                'name':self.model._fields[f].name,
                'label':self.model._fields[f].string,
                'type':self.model._fields[f].type,
            }forfinfields]

        #exportfirstwithoutthemockedspreadsheet,justtoensureitdoesn'tcrash
        self.url_open('/web/export/xlsx',data={
            'data':json.dumps(dict(self.default_params,**params)),
            'token':'dummy',
            'csrf_token':http.WebRequest.csrf_token(self),
        })
        withpatch.object(ExportXlsxWriter,'write',self._mock_write):
            self.url_open('/web/export/xlsx',data={
                'data':json.dumps(dict(self.default_params,**params)),
                'token':'dummy',
                'csrf_token':http.WebRequest.csrf_token(self),
            })
        returnself.worksheet

    defassertExportEqual(self,value,expected):
        forrowinrange(len(expected)):
            forcolumninrange(len(expected[row])):
                cell_value=value.pop((row,column),'')
                expected_value=expected[row][column]
                self.assertEqual(cell_value,expected_value,"Cell%s,%shaveawrongvalue"%(row,column))
        self.assertFalse(value,"Thereareunexpectedcellsintheexport")


@tagged('-at_install','post_install')
classTestGroupedExport(XlsxCreatorCase):
    model_name='export.group_operator'
    #pylint:disable=bad-whitespace

    deftest_int_sum_max(self):
        values=[
            {'int_sum':10,'int_max':20},
            {'int_sum':10,'int_max':50},
            {'int_sum':20,'int_max':30},
        ]
        export=self.export(values,fields=['int_sum','int_max'],params={'groupby':['int_sum','int_max']})
        self.assertExportEqual(export,[
            ['IntSum'     ,'IntMax'],
            ['10(2)'      ,'50'],
            ['   20(1)'  ,'20'],
            ['10'          ,'20'],
            ['   50(1)'  ,'50'],
            ['10'          ,'50'],
            ['20(1)'      ,'30'],
            ['   30(1)'  ,'30'],
            ['20'          ,'30'],
        ])

        export=self.export([],fields=['int_max','int_sum'],params={'groupby':['int_sum','int_max']})

        self.assertExportEqual(export,[
            ['IntMax'     ,'IntSum'],
            ['10(2)'      ,'20'],
            ['   20(1)'  ,'10'],
            ['20'          ,'10'],
            ['   50(1)'  ,'10'],
            ['50'          ,'10'],
            ['20(1)'      ,'20'],
            ['   30(1)'  ,'20'],
            ['30'          ,'20'],
        ])

    deftest_float_min(self):
        values=[
            {'int_sum':10,'float_min':111.0},
            {'int_sum':10,'float_min':222.0},
            {'int_sum':20,'float_min':333.0},
        ]
        export=self.export(values,fields=['int_sum','float_min'],params={'groupby':['int_sum','float_min']})

        self.assertExportEqual(export,[
            ['IntSum'     ,'FloatMin'],
            ['10(2)'      ,'111.00'],
            ['   111.0(1)','111.00'],
            ['10'          ,'111.00'],
            ['   222.0(1)','222.00'],
            ['10'          ,'222.00'],
            ['20(1)'      ,'333.00'],
            ['   333.0(1)','333.00'],
            ['20'          ,'333.00'],
        ])

    deftest_float_avg(self):
        values=[
            {'int_sum':10,'float_avg':100.0},
            {'int_sum':10,'float_avg':200.0},
            {'int_sum':20,'float_avg':300.0},
        ]
        export=self.export(values,fields=['int_sum','float_avg'],params={'groupby':['int_sum','float_avg']})

        self.assertExportEqual(export,[
            ['IntSum'     ,'FloatAvg'],
            ['10(2)'      ,'150.00'],
            ['   100.0(1)','100.00'],
            ['10'          ,'100.00'],
            ['   200.0(1)','200.00'],
            ['10'          ,'200.00'],
            ['20(1)'      ,'300.00'],
            ['   300.0(1)','300.00'],
            ['20'          ,'300.00'],
        ])

    deftest_float_avg_nested(self):
        """Withmorethanonenestedlevel(avgaggregation)"""
        values=[
            {'int_sum':10,'int_max':30,'float_avg':100.0},
            {'int_sum':10,'int_max':30,'float_avg':200.0},
            {'int_sum':10,'int_max':20,'float_avg':600.0},
        ]
        export=self.export(values,fields=['int_sum','float_avg'],params={'groupby':['int_sum','int_max','float_avg']})

        self.assertExportEqual(export,[
            ['IntSum'         ,'FloatAvg'],
            ['10(3)'          ,'300.00'],
            ['   20(1)'      ,'600.00'],
            ['       600.0(1)','600.00'],
            ['10'              ,'600.00'],
            ['   30(2)'      ,'150.00'],
            ['       100.0(1)','100.00'],
            ['10'              ,'100.00'],
            ['       200.0(1)','200.00'],
            ['10'              ,'200.00'],
        ])

    deftest_float_avg_nested_no_value(self):
        """Withmorethanonenestedlevel(avgaggregationisdoneon0,notFalse)"""
        values=[
            {'int_sum':10,'int_max':20,'float_avg':False},
            {'int_sum':10,'int_max':30,'float_avg':False},
            {'int_sum':10,'int_max':30,'float_avg':False},
        ]
        export=self.export(values,fields=['int_sum','float_avg'],params={'groupby':['int_sum','int_max','float_avg']})

        self.assertExportEqual(export,[
            ['IntSum'             ,'FloatAvg'],
            ['10(3)'              ,'0.00'],
            ['   20(1)'          ,'0.00'],
            ['       Undefined(1)','0.00'],
            ['10'                  ,'0.00'],
            ['   30(2)'          ,'0.00'],
            ['       Undefined(2)','0.00'],
            ['10'                  ,'0.00'],
            ['10'                  ,'0.00'],
        ])

    deftest_date_max(self):
        values=[
            {'int_sum':10,'date_max':date(2019,1,1)},
            {'int_sum':10,'date_max':date(2000,1,1)},
            {'int_sum':20,'date_max':date(1980,1,1)},
        ]
        export=self.export(values,fields=['int_sum','date_max'],params={'groupby':['int_sum','date_max:month']})

        self.assertExportEqual(export,[
            ['IntSum'             ,'DateMax'],
            ['10(2)'              ,'2019-01-01'],
            ['   January2000(1)','2000-01-01'],
            ['10'                  ,'2000-01-01'],
            ['   January2019(1)','2019-01-01'],
            ['10'                  ,'2019-01-01'],
            ['20(1)'              ,'1980-01-01'],
            ['   January1980(1)','1980-01-01'],
            ['20'                  ,'1980-01-01'],
        ])

    deftest_bool_and(self):
        values=[
            {'int_sum':10,'bool_and':True},
            {'int_sum':10,'bool_and':True},
            {'int_sum':20,'bool_and':True},
            {'int_sum':20,'bool_and':False},
        ]
        export=self.export(values,fields=['int_sum','bool_and'],params={'groupby':['int_sum','bool_and']})

        self.assertExportEqual(export,[
            ['IntSum'             ,'BoolAnd'],
            ['10(2)'              ,'True'],
            ['   True(2)'        ,'True'],
            ['10'                  ,'True'],
            ['10'                  ,'True'],
            ['20(2)'              ,'False'],
            ['   False(1)'       ,'False'],
            ['20'                  ,'False'],
            ['   True(1)'        ,'True'],
            ['20'                  ,'True'],
        ])

    deftest_bool_or(self):
        values=[
            {'int_sum':10,'bool_or':True},
            {'int_sum':10,'bool_or':False},
            {'int_sum':20,'bool_or':False},
            {'int_sum':20,'bool_or':False},
        ]
        export=self.export(values,fields=['int_sum','bool_or'],params={'groupby':['int_sum','bool_or']})

        self.assertExportEqual(export,[
            ['IntSum'             ,'BoolOr'],
            ['10(2)'              ,'True'],
            ['   False(1)'       ,'False'],
            ['10'                  ,'False'],
            ['   True(1)'        ,'True'],
            ['10'                  ,'True'],
            ['20(2)'              ,'False'],
            ['   False(2)'       ,'False'],
            ['20'                  ,'False'],
            ['20'                  ,'False'],
        ])

    deftest_many2one(self):
        values=[
            {'int_sum':10,'many2one':self.env['export.integer'].create({}).id},
            {'int_sum':10},
        ]
        export=self.export(values,fields=['int_sum','many2one'],params={'groupby':['int_sum','many2one']})

        self.assertExportEqual(export,[
            ['IntSum'                 ,'Many2One'],
            ['10(2)'                  ,''],
            ['   export.integer:4(1)',''],
            ['10'                      ,'export.integer:4'],
            ['   Undefined(1)'       ,''],
            ['10'                      ,''],
        ])

    deftest_nested_records(self):
        """
        aggregatedvaluescurrentlynotsupportedfornestedrecordexport,butitshouldnotcrash
        e.g.export'many2one/const'
        """
        values=[{'int_sum':10,
            'date_max':date(2019,1,1),
            'many2one':self.env['export.integer'].create({}).id,
        },{
            'int_sum':10,
            'date_max':date(2000,1,1),
            'many2one':self.env['export.integer'].create({}).id,
        },]
        export=self.export(values,
                    params={
                        'groupby':['int_sum','date_max:month'],
                        'fields':[
                            {'name':'int_sum','label':'IntSum'},
                            {'name':'date_max','label':'DateMax'},
                            {'name':'many2one/value','label':'Many2One/Value'},
                        ]
                    })

        self.assertExportEqual(export,[
            ['IntSum'             ,'DateMax'    ,'Many2One/Value'],
            ['10(2)'              ,'2019-01-01'  ,''],
            ['   January2000(1)','2000-01-01'  ,''],
            ['10'                  ,'2000-01-01'  ,'4'],
            ['   January2019(1)','2019-01-01'  ,''],
            ['10'                  ,'2019-01-01'  ,'4'],
        ])

    deftest_one2many(self):
        values=[{
            'int_sum':10,
            'one2many':[
                (0,0,{'value':8}),
                (0,0,{'value':9}),
            ],
        }]
        export=self.export(values,
                    params={
                        'groupby':['int_sum',],
                        'fields':[
                            {'name':'int_sum','label':'IntSum'},
                            {'name':'one2many/value','label':'One2many/Value'},
                        ]
                    })
        self.assertExportEqual(export,[
            ['IntSum' ,'One2many/Value'],
            ['10(1)'  ,''],
            ['10'      ,'8'],
            [''        ,'9'],
        ])

    deftest_unset_date_values(self):
        values=[
            {'int_sum':10,'date_max':date(2019,1,1)},
            {'int_sum':10,'date_max':False},
        ]
        #Groupandaggregatebydate,butdatefieldsarenotsetforallrecords
        export=self.export(values,fields=['int_sum','date_max'],params={'groupby':['int_sum','date_max:month']})

        self.assertExportEqual(export,[
            ['IntSum'             ,'DateMax'],
            ['10(2)'              ,'2019-01-01'],
            ['   January2019(1)','2019-01-01'],
            ['10'                  ,'2019-01-01'],
            ['   Undefined(1)'   ,''],
            ['10'                  ,''],
        ])

    deftest_float_representation(self):
        currency=self.env['res.currency'].create({
            'name':"bottlecap",
            'symbol':"b",
            'rounding':0.001,
            'decimal_places':3,
        })

        values=[
                {'int_sum':1,'currency_id':currency.id,'float_monetary':60739.2000000004},
                {'int_sum':2,'currency_id':currency.id,'float_monetary':2.0},
                {'int_sum':3,'currency_id':currency.id,'float_monetary':999.9995999},
        ]
        export=self.export(values,fields=['int_sum','float_monetary'],params={'groupby':['int_sum','float_monetary']})

        self.assertExportEqual(export,[
            ['IntSum','FloatMonetary'],
            ['1(1)','60739.200'],
            ['   60739.2(1)','60739.200'],
            ['1','60739.20'],
            ['2(1)','2.000'],
            ['   2.0(1)','2.000'],
            ['2','2.00'],
            ['3(1)','1000.000'],
            ['   1000.0(1)','1000.000'],
            ['3','1000.00'],
        ])

    deftest_decimal_separator(self):
        """Thedecimalseparatorofthelanguageusedshouldn'timpactthefloatrepresentationintheexportedxlsx"""
        get_lang(self.env).decimal_point=','
        get_lang(self.env).thousands_sep='.'

        values=[
                {'int_sum':1,'float_min':86420.864},
        ]
        export=self.export(values,fields=['int_sum','float_min'],params={'groupby':['int_sum','float_min']})

        self.assertExportEqual(export,[
            ['IntSum'         ,'FloatMin'],
            ['1(1)'           ,'86420.86'],
            ['   86420.864(1)','86420.86'],
            ['1'               ,'86420.86'],
        ])

@tagged('-at_install','post_install')
classTestComputedBinaryExport(XlsxCreatorCase):
    model_name='export.computed.binary'

    deftest_grouped_computed_binary(self):
        values=[{}]
        export=self.export(values,fields=['binary_field'],params={'groupby':['create_uid']})
        self.assertExportEqual(export,[
            ['BinaryField'],
            ['FlectraBot(1)'],
            ["['computedvalue']"],
        ])
