#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_


classJob(models.Model):

    _name="hr.job"
    _description="JobPosition"
    _inherit=['mail.thread']

    name=fields.Char(string='JobPosition',required=True,index=True,translate=True)
    expected_employees=fields.Integer(compute='_compute_employees',string='TotalForecastedEmployees',store=True,
        help='Expectednumberofemployeesforthisjobpositionafternewrecruitment.')
    no_of_employee=fields.Integer(compute='_compute_employees',string="CurrentNumberofEmployees",store=True,
        help='Numberofemployeescurrentlyoccupyingthisjobposition.')
    no_of_recruitment=fields.Integer(string='ExpectedNewEmployees',copy=False,
        help='Numberofnewemployeesyouexpecttorecruit.',default=1)
    no_of_hired_employee=fields.Integer(string='HiredEmployees',copy=False,
        help='Numberofhiredemployeesforthisjobpositionduringrecruitmentphase.')
    employee_ids=fields.One2many('hr.employee','job_id',string='Employees',groups='base.group_user')
    description=fields.Text(string='JobDescription')
    requirements=fields.Text('Requirements')
    department_id=fields.Many2one('hr.department',string='Department',domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    company_id=fields.Many2one('res.company',string='Company',default=lambdaself:self.env.company)
    state=fields.Selection([
        ('recruit','RecruitmentinProgress'),
        ('open','NotRecruiting')
    ],string='Status',readonly=True,required=True,tracking=True,copy=False,default='recruit',help="Setwhethertherecruitmentprocessisopenorclosedforthisjobposition.")

    _sql_constraints=[
        ('name_company_uniq','unique(name,company_id,department_id)','Thenameofthejobpositionmustbeuniqueperdepartmentincompany!'),
    ]

    @api.depends('no_of_recruitment','employee_ids.job_id','employee_ids.active')
    def_compute_employees(self):
        employee_data=self.env['hr.employee'].read_group([('job_id','in',self.ids)],['job_id'],['job_id'])
        result=dict((data['job_id'][0],data['job_id_count'])fordatainemployee_data)
        forjobinself:
            job.no_of_employee=result.get(job.id,0)
            job.expected_employees=result.get(job.id,0)+job.no_of_recruitment

    @api.model
    defcreate(self,values):
        """Wedon'twantthecurrentusertobefollowerofallcreatedjob"""
        returnsuper(Job,self.with_context(mail_create_nosubscribe=True)).create(values)

    @api.returns('self',lambdavalue:value.id)
    defcopy(self,default=None):
        self.ensure_one()
        default=dict(defaultor{})
        if'name'notindefault:
            default['name']=_("%s(copy)")%(self.name)
        returnsuper(Job,self).copy(default=default)

    defset_recruit(self):
        forrecordinself:
            no_of_recruitment=1ifrecord.no_of_recruitment==0elserecord.no_of_recruitment
            record.write({'state':'recruit','no_of_recruitment':no_of_recruitment})
        returnTrue

    defset_open(self):
        returnself.write({
            'state':'open',
            'no_of_recruitment':0,
            'no_of_hired_employee':0
        })
