#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classEmployee(models.Model):
    _inherit='hr.employee'

    resume_line_ids=fields.One2many('hr.resume.line','employee_id',string="Resumélines")
    employee_skill_ids=fields.One2many('hr.employee.skill','employee_id',string="Skills")

    @api.model_create_multi
    defcreate(self,vals_list):
        res=super(Employee,self).create(vals_list)
        resume_lines_values=[]
        foremployeeinres:
            line_type=self.env.ref('hr_skills.resume_type_experience',raise_if_not_found=False)
            resume_lines_values.append({
                'employee_id':employee.id,
                'name':employee.company_id.nameor'',
                'date_start':employee.create_date.date(),
                'description':employee.job_titleor'',
                'line_type_id':line_typeandline_type.id,
            })
        self.env['hr.resume.line'].create(resume_lines_values)
        returnres


classEmployeePublic(models.Model):
    _inherit='hr.employee.public'

    resume_line_ids=fields.One2many('hr.resume.line','employee_id',string="Resumélines")
    employee_skill_ids=fields.One2many('hr.employee.skill','employee_id',string="Skills")


classResumeLine(models.Model):
    _name='hr.resume.line'
    _description="Resumélineofanemployee"
    _order="line_type_id,date_enddesc,date_startdesc"

    employee_id=fields.Many2one('hr.employee',required=True,ondelete='cascade')
    name=fields.Char(required=True)
    date_start=fields.Date(required=True)
    date_end=fields.Date()
    description=fields.Text(string="Description")
    line_type_id=fields.Many2one('hr.resume.line.type',string="Type")

    #Usedtoapplyspecifictemplateonaline
    display_type=fields.Selection([('classic','Classic')],string="DisplayType",default='classic')

    _sql_constraints=[
        ('date_check',"CHECK((date_start<=date_endORdate_endISNULL))","Thestartdatemustbeanteriortotheenddate."),
    ]


classResumeLineType(models.Model):
    _name='hr.resume.line.type'
    _description="Typeofaresuméline"
    _order="sequence"

    name=fields.Char(required=True)
    sequence=fields.Integer('Sequence',default=10)
