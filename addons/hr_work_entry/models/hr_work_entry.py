#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcontextlibimportcontextmanager
fromdateutil.relativedeltaimportrelativedelta
importitertools
frompsycopg2importOperationalError

fromflectraimportapi,fields,models,tools


classHrWorkEntry(models.Model):
    _name='hr.work.entry'
    _description='HRWorkEntry'
    _order='conflictdesc,state,date_start'

    name=fields.Char(required=True)
    active=fields.Boolean(default=True)
    employee_id=fields.Many2one('hr.employee',required=True,domain="['|',('company_id','=',False),('company_id','=',company_id)]",index=True)
    date_start=fields.Datetime(required=True,string='From')
    date_stop=fields.Datetime(compute='_compute_date_stop',store=True,readonly=False,string='To')
    duration=fields.Float(compute='_compute_duration',store=True,string="Period")
    work_entry_type_id=fields.Many2one('hr.work.entry.type',index=True)
    color=fields.Integer(related='work_entry_type_id.color',readonly=True)
    state=fields.Selection([
        ('draft','Draft'),
        ('validated','Validated'),
        ('conflict','Conflict'),
        ('cancelled','Cancelled')
    ],default='draft')
    company_id=fields.Many2one('res.company',string='Company',readonly=True,required=True,
        default=lambdaself:self.env.company)
    conflict=fields.Boolean('Conflicts',compute='_compute_conflict',store=True) #Usedtoshowconflictingworkentriesfirst

    _sql_constraints=[
        ('_work_entry_has_end','check(date_stopISNOTNULL)','Workentrymustend.Pleasedefineanenddateoraduration.'),
        ('_work_entry_start_before_end','check(date_stop>date_start)','Startingtimeshouldbebeforeendtime.')
    ]

    definit(self):
        tools.create_index(self._cr,"hr_work_entry_date_start_date_stop_index",self._table,["date_start","date_stop"])

    @api.depends('state')
    def_compute_conflict(self):
        forrecinself:
            rec.conflict=rec.state=='conflict'

    @api.depends('date_stop','date_start')
    def_compute_duration(self):
        forwork_entryinself:
            work_entry.duration=work_entry._get_duration(work_entry.date_start,work_entry.date_stop)

    @api.depends('date_start','duration')
    def_compute_date_stop(self):
        forwork_entryinself.filtered(lambdaw:w.date_startandw.duration):
            work_entry.date_stop=work_entry.date_start+relativedelta(hours=work_entry.duration)

    def_get_duration(self,date_start,date_stop):
        ifnotdate_startornotdate_stop:
            return0
        dt=date_stop-date_start
        returndt.days*24+dt.seconds/3600 #Numberofhours

    defaction_validate(self):
        """
        Trytovalidateworkentries.
        Ifsomeerrorsarefound,set`state`toconflictforconflictingworkentries
        andvalidationfails.
        :return:Trueifvalidationsucceded
        """
        work_entries=self.filtered(lambdawork_entry:work_entry.state!='validated')
        ifnotwork_entries._check_if_error():
            work_entries.write({'state':'validated'})
            returnTrue
        returnFalse

    def_check_if_error(self):
        ifnotself:
            returnFalse
        undefined_type=self.filtered(lambdab:notb.work_entry_type_id)
        undefined_type.write({'state':'conflict'})
        conflict=self._mark_conflicting_work_entries(min(self.mapped('date_start')),max(self.mapped('date_stop')))
        returnundefined_typeorconflict

    def_mark_conflicting_work_entries(self,start,stop):
        """
        Set`state`to`conflict`foroverlappingworkentries
        betweentwodates.
        If`self.ids`istruthythencheckconflictswiththecorrespondingworkentries.
        ReturnTrueifoverlappingworkentriesweredetected.
        """
        #Usethepostgresqlrangetype`tsrange`whichisarangeoftimestamp
        #Itsupportstheintersectionoperator(&&)usefultodetectoverlap.
        #use'()'toexludethelowerandupperboundsoftherange.
        #Filterondate_startanddate_stop(bothindexed)intheEXISTSclauseto
        #limittheresultingsetsizeandfastenthequery.
        self.flush(['date_start','date_stop','employee_id','active'])
        query="""
            SELECTb1.id,
                   b2.id
              FROMhr_work_entryb1
              JOINhr_work_entryb2
                ONb1.employee_id=b2.employee_id
               ANDb1.id<>b2.id
             WHEREb1.date_start<=%(stop)s
               ANDb1.date_stop>=%(start)s
               ANDb1.active=TRUE
               ANDb2.active=TRUE
               ANDtsrange(b1.date_start,b1.date_stop,'()')&&tsrange(b2.date_start,b2.date_stop,'()')
               AND{}
        """.format("b2.idIN%(ids)s"ifself.idselse"b2.date_start<=%(stop)sANDb2.date_stop>=%(start)s")
        self.env.cr.execute(query,{"stop":stop,"start":start,"ids":tuple(self.ids)})
        conflicts=set(itertools.chain.from_iterable(self.env.cr.fetchall()))
        self.browse(conflicts).write({
            'state':'conflict',
        })
        returnbool(conflicts)

    @api.model_create_multi
    defcreate(self,vals_list):
        work_entries=super().create(vals_list)
        work_entries._check_if_error()
        returnwork_entries

    defwrite(self,vals):
        skip_check=notbool({'date_start','date_stop','employee_id','work_entry_type_id','active'}&vals.keys())
        if'state'invals:
            ifvals['state']=='draft':
                vals['active']=True
            elifvals['state']=='cancelled':
                vals['active']=False
                skip_check&=all(self.mapped(lambdaw:w.state!='conflict'))

        if'active'invals:
            vals['state']='draft'ifvals['active']else'cancelled'

        withself._error_checking(skip=skip_check):
            returnsuper(HrWorkEntry,self).write(vals)

    defunlink(self):
        withself._error_checking():
            returnsuper().unlink()

    def_reset_conflicting_state(self):
        self.filtered(lambdaw:w.state=='conflict').write({'state':'draft'})

    @contextmanager
    def_error_checking(self,start=None,stop=None,skip=False):
        """
        Contextmanagerusedforconflictschecking.
        Whenexitingthecontextmanager,conflictsarechecked
        forallworkentrieswithinadaterange.Bydefault,thestartandenddatesare
        computedaccordingto`self`(minandmaxrespectively)butitcanbeoverwrittenbyproviding
        othervaluesasparameter.
        :paramstart:datetimetooverwritethedefaultbehaviour
        :paramstop:datetimetooverwritethedefaultbehaviour
        :paramskip:IfTrue,noerrorcheckingisdone
        """
        try:
            skip=skiporself.env.context.get('hr_work_entry_no_check',False)
            start=startormin(self.mapped('date_start'),default=False)
            stop=stopormax(self.mapped('date_stop'),default=False)
            ifnotskipandstartandstop:
                work_entries=self.sudo().with_context(hr_work_entry_no_check=True).search([
                    ('date_start','<',stop),
                    ('date_stop','>',start),
                    ('state','notin',('validated','cancelled')),
                ])
                work_entries._reset_conflicting_state()
            yield
        exceptOperationalError:
            #thecursorisdead,donotattempttouseitorwewillshadowtherootexception
            #witha"psycopg2.InternalError:currenttransactionisaborted,..."
            skip=True
            raise
        finally:
            ifnotskipandstartandstop:
                #Newworkentriesarehandledinthecreatemethod,
                #noneedtoreloadworkentries.
                work_entries.exists()._check_if_error()


classHrWorkEntryType(models.Model):
    _name='hr.work.entry.type'
    _description='HRWorkEntryType'

    name=fields.Char(required=True,translate=True)
    code=fields.Char(required=True)
    color=fields.Integer(default=0)
    sequence=fields.Integer(default=25)
    active=fields.Boolean(
        'Active',default=True,
        help="Iftheactivefieldissettofalse,itwillallowyoutohidetheworkentrytypewithoutremovingit.")

    _sql_constraints=[
        ('unique_work_entry_code','UNIQUE(code)','Thesamecodecannotbeassociatedtomultipleworkentrytypes.'),
    ]


classContacts(models.Model):
    """Personnalcalendarfilter"""

    _name='hr.user.work.entry.employee'
    _description='WorkEntriesEmployees'

    user_id=fields.Many2one('res.users','Me',required=True,default=lambdaself:self.env.user)
    employee_id=fields.Many2one('hr.employee','Employee',required=True)
    active=fields.Boolean('Active',default=True)

    _sql_constraints=[
        ('user_id_employee_id_unique','UNIQUE(user_id,employee_id)','Youcannothavethesameemployeetwice.')
    ]
