#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.testsimportcommon


@common.tagged('post_install','-at_install')
classTestReadProgressBar(common.TransactionCase):
    """Testforread_progress_bar"""

    defsetUp(self):
        super(TestReadProgressBar,self).setUp()
        self.Model=self.env['res.partner']

    deftest_week_grouping(self):
        """Thelabelsassociatedtoeachrecordinread_progress_barshouldmatch
        theonesfromread_group,eveninedgecaseslikeen_USlocaleonsundays
        """
        context={"lang":"en_US"}
        groupby="date:week"
        self.Model.create({'date':'2021-05-02','name':"testWeekGrouping_first"})#Sunday
        self.Model.create({'date':'2021-05-09','name':"testWeekGrouping_second"})#Sunday
        progress_bar={
            'field':'name',
            'colors':{
                "testWeekGrouping_first":'success',
                "testWeekGrouping_second":'danger',
            }
        }
        
        groups=self.Model.with_context(context).read_group(
            [('name',"like","testWeekGrouping%")],fields=['date','name'],groupby=[groupby])
        progressbars=self.Model.with_context(context).read_progress_bar(
            [('name',"like","testWeekGrouping%")],group_by=groupby,progress_bar=progress_bar)
        self.assertEqual(len(groups),2)
        self.assertEqual(len(progressbars),2)

        #formattheread_progress_barresulttogetadictionaryunderthisformat:{record_name:group_name}
        #originalformat(afterread_progress_bar)is:{group_name:{record_name:count}}
        pg_groups={
            next(record_nameforrecord_name,countindata.items()ifcount):group_name\
                forgroup_name,datainprogressbars.items()
        }

        self.assertEqual(groups[0][groupby],pg_groups["testWeekGrouping_first"])
        self.assertEqual(groups[1][groupby],pg_groups["testWeekGrouping_second"])

    deftest_simple(self):
        model=self.env['ir.model'].create({
            'model':'x_progressbar',
            'name':'progress_bar',
            'field_id':[
                (0,0,{
                    'field_description':'Country',
                    'name':'x_country_id',
                    'ttype':'many2one',
                    'relation':'res.country',
                }),
                (0,0,{
                    'field_description':'Date',
                    'name':'x_date',
                    'ttype':'date',
                }),
                (0,0,{
                    'field_description':'State',
                    'name':'x_state',
                    'ttype':'selection',
                    'selection':"[('foo','Foo'),('bar','Bar'),('baz','Baz')]",
                }),
            ],
        })

        c1,c2,c3=self.env['res.country'].search([],limit=3)

        self.env['x_progressbar'].create([
            #week21
            {'x_country_id':c1.id,'x_date':'2021-05-20','x_state':'foo'},
            {'x_country_id':c1.id,'x_date':'2021-05-21','x_state':'foo'},
            {'x_country_id':c1.id,'x_date':'2021-05-22','x_state':'foo'},
            {'x_country_id':c1.id,'x_date':'2021-05-23','x_state':'bar'},
            #week22
            {'x_country_id':c1.id,'x_date':'2021-05-24','x_state':'baz'},
            {'x_country_id':c2.id,'x_date':'2021-05-25','x_state':'foo'},
            {'x_country_id':c2.id,'x_date':'2021-05-26','x_state':'bar'},
            {'x_country_id':c2.id,'x_date':'2021-05-27','x_state':'bar'},
            {'x_country_id':c2.id,'x_date':'2021-05-28','x_state':'baz'},
            {'x_country_id':c2.id,'x_date':'2021-05-29','x_state':'baz'},
            {'x_country_id':c3.id,'x_date':'2021-05-30','x_state':'foo'},
            #week23
            {'x_country_id':c3.id,'x_date':'2021-05-31','x_state':'foo'},
            {'x_country_id':c3.id,'x_date':'2021-06-01','x_state':'baz'},
            {'x_country_id':c3.id,'x_date':'2021-06-02','x_state':'baz'},
            {'x_country_id':c3.id,'x_date':'2021-06-03','x_state':'baz'},
        ])

        progress_bar={
            'field':'x_state',
            'colors':{'foo':'success','bar':'warning','baz':'danger'},
        }
        result=self.env['x_progressbar'].read_progress_bar([],'x_country_id',progress_bar)
        self.assertEqual(result,{
            c1.display_name:{'foo':3,'bar':1,'baz':1},
            c2.display_name:{'foo':1,'bar':2,'baz':2},
            c3.display_name:{'foo':2,'bar':0,'baz':3},
        })

        #checkdateaggregationandformat
        result=self.env['x_progressbar'].read_progress_bar([],'x_date:week',progress_bar)
        self.assertEqual(result,{
            'W212021':{'foo':3,'bar':1,'baz':0},
            'W222021':{'foo':2,'bar':2,'baz':3},
            'W232021':{'foo':1,'bar':0,'baz':3},
        })

        #addacomputedfieldonmodel
        model.write({'field_id':[
            (0,0,{
                'field_description':'RelatedState',
                'name':'x_state_computed',
                'ttype':'selection',
                'selection':"[('foo','Foo'),('bar','Bar'),('baz','Baz')]",
                'compute':"forrecinself:rec['x_state_computed']=rec.x_state",
                'depends':'x_state',
                'readonly':True,
                'store':False,
            }),
        ]})

        progress_bar={
            'field':'x_state_computed',
            'colors':{'foo':'success','bar':'warning','baz':'danger'},
        }
        result=self.env['x_progressbar'].read_progress_bar([],'x_country_id',progress_bar)
        self.assertEqual(result,{
            c1.display_name:{'foo':3,'bar':1,'baz':1},
            c2.display_name:{'foo':1,'bar':2,'baz':2},
            c3.display_name:{'foo':2,'bar':0,'baz':3},
        })

        result=self.env['x_progressbar'].read_progress_bar([],'x_date:week',progress_bar)
        self.assertEqual(result,{
            'W212021':{'foo':3,'bar':1,'baz':0},
            'W222021':{'foo':2,'bar':2,'baz':3},
            'W232021':{'foo':1,'bar':0,'baz':3},
        })
