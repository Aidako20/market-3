#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models
fromflectra.exceptionsimportValidationError

fromcalendarimportmonthrange
fromdateutil.relativedeltaimportrelativedelta
fromdateutil.rruleimportrrule,rruleset,DAILY,WEEKLY,MONTHLY,YEARLY,MO,TU,WE,TH,FR,SA,SU

MONTHS={
    'january':31,
    'february':28,
    'march':31,
    'april':30,
    'may':31,
    'june':30,
    'july':31,
    'august':31,
    'september':30,
    'october':31,
    'november':30,
    'december':31,
}

DAYS={
    'mon':MO,
    'tue':TU,
    'wed':WE,
    'thu':TH,
    'fri':FR,
    'sat':SA,
    'sun':SU,
}

WEEKS={
    'first':1,
    'second':2,
    'third':3,
    'last':4,
}

classProjectTaskRecurrence(models.Model):
    _name='project.task.recurrence'
    _description='TaskRecurrence'

    task_ids=fields.One2many('project.task','recurrence_id')
    next_recurrence_date=fields.Date()
    recurrence_left=fields.Integer(string="Numberoftaskslefttocreate")

    repeat_interval=fields.Integer(string='RepeatEvery',default=1)
    repeat_unit=fields.Selection([
        ('day','Days'),
        ('week','Weeks'),
        ('month','Months'),
        ('year','Years'),
    ],default='week')
    repeat_type=fields.Selection([
        ('forever','Forever'),
        ('until','EndDate'),
        ('after','NumberofRepetitions'),
    ],default="forever",string="Until")
    repeat_until=fields.Date(string="EndDate")
    repeat_number=fields.Integer(string="Repetitions")

    repeat_on_month=fields.Selection([
        ('date','DateoftheMonth'),
        ('day','DayoftheMonth'),
    ])

    repeat_on_year=fields.Selection([
        ('date','DateoftheYear'),
        ('day','DayoftheYear'),
    ])

    mon=fields.Boolean(string="Mon")
    tue=fields.Boolean(string="Tue")
    wed=fields.Boolean(string="Wed")
    thu=fields.Boolean(string="Thu")
    fri=fields.Boolean(string="Fri")
    sat=fields.Boolean(string="Sat")
    sun=fields.Boolean(string="Sun")

    repeat_day=fields.Selection([
        (str(i),str(i))foriinrange(1,32)
    ])
    repeat_week=fields.Selection([
        ('first','First'),
        ('second','Second'),
        ('third','Third'),
        ('last','Last'),
    ])
    repeat_weekday=fields.Selection([
        ('mon','Monday'),
        ('tue','Tuesday'),
        ('wed','Wednesday'),
        ('thu','Thursday'),
        ('fri','Friday'),
        ('sat','Saturday'),
        ('sun','Sunday'),
    ],string='DayOfTheWeek',readonly=False)
    repeat_month=fields.Selection([
        ('january','January'),
        ('february','February'),
        ('march','March'),
        ('april','April'),
        ('may','May'),
        ('june','June'),
        ('july','July'),
        ('august','August'),
        ('september','September'),
        ('october','October'),
        ('november','November'),
        ('december','December'),
    ])

    @api.constrains('repeat_unit','mon','tue','wed','thu','fri','sat','sun')
    def_check_recurrence_days(self):
        forprojectinself.filtered(lambdap:p.repeat_unit=='week'):
            ifnotany([project.mon,project.tue,project.wed,project.thu,project.fri,project.sat,project.sun]):
                raiseValidationError('Youshouldselectaleastoneday')

    @api.constrains('repeat_interval')
    def_check_repeat_interval(self):
        ifself.filtered(lambdat:t.repeat_interval<=0):
            raiseValidationError('Theintervalshouldbegreaterthan0')

    @api.constrains('repeat_number','repeat_type')
    def_check_repeat_number(self):
        ifself.filtered(lambdat:t.repeat_type=='after'andt.repeat_number<=0):
            raiseValidationError('Shouldrepeatatleastonce')

    @api.constrains('repeat_type','repeat_until')
    def_check_repeat_until_date(self):
        today=fields.Date.today()
        ifself.filtered(lambdat:t.repeat_type=='until'andt.repeat_until<today):
            raiseValidationError('Theenddateshouldbeinthefuture')

    @api.constrains('repeat_unit','repeat_on_month','repeat_day','repeat_type','repeat_until')
    def_check_repeat_until_month(self):
        ifself.filtered(lambdar:r.repeat_type=='until'andr.repeat_unit=='month'andr.repeat_untilandr.repeat_on_month=='date'
           andint(r.repeat_day)>r.repeat_until.dayandmonthrange(r.repeat_until.year,r.repeat_until.month)[1]!=r.repeat_until.day):
            raiseValidationError('Theenddateshouldbeafterthedayofthemonthorthelastdayofthemonth')

    @api.model
    def_get_recurring_fields(self):
        return['allowed_user_ids','company_id','description','displayed_image_id','email_cc',
                'parent_id','partner_email','partner_id','partner_phone','planned_hours',
                'project_id','project_privacy_visibility','sequence','tag_ids','recurrence_id',
                'name','recurring_task']

    def_get_weekdays(self,n=1):
        self.ensure_one()
        ifself.repeat_unit=='week':
            return[fn(n)forday,fninDAYS.items()ifself[day]]
        return[DAYS.get(self.repeat_weekday)(n)]

    @api.model
    def_get_next_recurring_dates(self,date_start,repeat_interval,repeat_unit,repeat_type,repeat_until,repeat_on_month,repeat_on_year,weekdays,repeat_day,repeat_week,repeat_month,**kwargs):
        count=kwargs.get('count',1)
        rrule_kwargs={'interval':repeat_intervalor1,'dtstart':date_start}
        repeat_day=int(repeat_day)
        start=False
        dates=[]
        ifrepeat_type=='until':
            rrule_kwargs['until']=repeat_untilifrepeat_untilelsefields.Date.today()
        else:
            rrule_kwargs['count']=count

        ifrepeat_unit=='week'\
            or(repeat_unit=='month'andrepeat_on_month=='day')\
            or(repeat_unit=='year'andrepeat_on_year=='day'):
            rrule_kwargs['byweekday']=weekdays

        ifrepeat_unit=='day':
            rrule_kwargs['freq']=DAILY
        elifrepeat_unit=='month':
            rrule_kwargs['freq']=MONTHLY
            ifrepeat_on_month=='date':
                start=date_start-relativedelta(days=1)
                start=start.replace(day=min(repeat_day,monthrange(start.year,start.month)[1]))
                ifstart<date_start:
                    #Ensurethenextrecurrenceisinthefuture
                    start+=relativedelta(months=repeat_interval)
                    start=start.replace(day=min(repeat_day,monthrange(start.year,start.month)[1]))
                can_generate_date=(lambda:start<=repeat_until)ifrepeat_type=='until'else(lambda:len(dates)<count)
                whilecan_generate_date():
                    dates.append(start)
                    start+=relativedelta(months=repeat_interval)
                    start=start.replace(day=min(repeat_day,monthrange(start.year,start.month)[1]))
                returndates
        elifrepeat_unit=='year':
            rrule_kwargs['freq']=YEARLY
            month=list(MONTHS.keys()).index(repeat_month)+1
            rrule_kwargs['bymonth']=month
            ifrepeat_on_year=='date':
                rrule_kwargs['bymonthday']=min(repeat_day,MONTHS.get(repeat_month))
                rrule_kwargs['bymonth']=month
        else:
            rrule_kwargs['freq']=WEEKLY

        rules=rrule(**rrule_kwargs)
        returnlist(rules)ifruleselse[]

    def_new_task_values(self,task):
        self.ensure_one()
        fields_to_copy=self._get_recurring_fields()
        task_values=task.read(fields_to_copy).pop()
        create_values={
            field:value[0]ifisinstance(value,tuple)elsevalueforfield,valueintask_values.items()
        }
        create_values['stage_id']=task.project_id.type_ids[0].idiftask.project_id.type_idselsetask.stage_id.id
        create_values['user_id']=False
        returncreate_values

    def_create_next_task(self):
        forrecurrenceinself:
            task=max(recurrence.sudo().task_ids,key=lambdat:t.id)
            create_values=recurrence._new_task_values(task)
            new_task=self.env['project.task'].sudo().create(create_values)
            ifnotnew_task.parent_idandtask.child_ids:
                children=[]
                #copythesubtasksoftheoriginaltask
                forchildintask.child_ids:
                    child_values=recurrence._new_task_values(child)
                    child_values['parent_id']=new_task.id
                    children.append(child_values)
                self.env['project.task'].create(children)

    def_set_next_recurrence_date(self):
        today=fields.Date.today()
        tomorrow=today+relativedelta(days=1)
        forrecurrenceinself.filtered(
            lambdar:
            r.repeat_type=='after'andr.recurrence_left>=0
            orr.repeat_type=='until'andr.repeat_until>=today
            orr.repeat_type=='forever'
        ):
            ifrecurrence.repeat_type=='after'andrecurrence.recurrence_left==0:
                recurrence.next_recurrence_date=False
            else:
                next_date=self._get_next_recurring_dates(tomorrow,recurrence.repeat_interval,recurrence.repeat_unit,recurrence.repeat_type,recurrence.repeat_until,recurrence.repeat_on_month,recurrence.repeat_on_year,recurrence._get_weekdays(),recurrence.repeat_day,recurrence.repeat_week,recurrence.repeat_month,count=1)
                recurrence.next_recurrence_date=next_date[0]ifnext_dateelseFalse

    @api.model
    def_cron_create_recurring_tasks(self):
        ifnotself.env.user.has_group('project.group_project_recurring_tasks'):
            return
        today=fields.Date.today()
        recurring_today=self.search([('next_recurrence_date','<=',today)])
        recurring_today._create_next_task()
        forrecurrenceinrecurring_today.filtered(lambdar:r.repeat_type=='after'):
            recurrence.recurrence_left-=1
        recurring_today._set_next_recurrence_date()

    @api.model
    defcreate(self,vals):
        ifvals.get('repeat_number'):
            vals['recurrence_left']=vals.get('repeat_number')
        res=super(ProjectTaskRecurrence,self).create(vals)
        res._set_next_recurrence_date()
        returnres

    defwrite(self,vals):
        ifvals.get('repeat_number'):
            vals['recurrence_left']=vals.get('repeat_number')

        res=super(ProjectTaskRecurrence,self).write(vals)

        if'next_recurrence_date'notinvals:
            self._set_next_recurrence_date()
        returnres
