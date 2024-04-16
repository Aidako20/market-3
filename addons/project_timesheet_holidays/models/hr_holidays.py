#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError


classHolidaysType(models.Model):
    _inherit="hr.leave.type"

    def_default_project_id(self):
        company=self.company_idifself.company_idelseself.env.company
        returncompany.leave_timesheet_project_id.id

    def_default_task_id(self):
        company=self.company_idifself.company_idelseself.env.company
        returncompany.leave_timesheet_task_id.id

    timesheet_generate=fields.Boolean(
        'GenerateTimesheet',compute='_compute_timesheet_generate',store=True,readonly=False,
        help="Ifchecked,whenvalidatingatimeoff,timesheetwillbegeneratedintheVacationProjectofthecompany.")
    timesheet_project_id=fields.Many2one('project.project',string="Project",default=_default_project_id,domain="[('company_id','=',company_id)]",help="Theprojectwillcontainthetimesheetgeneratedwhenatimeoffisvalidated.")
    timesheet_task_id=fields.Many2one(
        'project.task',string="Taskfortimesheet",compute='_compute_timesheet_task_id',
        store=True,readonly=False,default=_default_task_id,
        domain="[('project_id','=',timesheet_project_id),"
                "('company_id','=',company_id)]")

    @api.depends('timesheet_task_id','timesheet_project_id')
    def_compute_timesheet_generate(self):
        forleave_typeinself:
            leave_type.timesheet_generate=leave_type.timesheet_task_idandleave_type.timesheet_project_id

    @api.depends('timesheet_project_id')
    def_compute_timesheet_task_id(self):
        forleave_typeinself:
            company=leave_type.company_idifleave_type.company_idelseself.env.company
            default_task_id=company.leave_timesheet_task_id

            ifdefault_task_idanddefault_task_id.project_id==leave_type.timesheet_project_id:
                leave_type.timesheet_task_id=default_task_id
            else:
                leave_type.timesheet_task_id=False

    @api.constrains('timesheet_generate','timesheet_project_id','timesheet_task_id')
    def_check_timesheet_generate(self):
        forholiday_statusinself:
            ifholiday_status.timesheet_generate:
                ifnotholiday_status.timesheet_project_idornotholiday_status.timesheet_task_id:
                    raiseValidationError(_("Boththeinternalprojectandtaskarerequiredto"
                    "generateatimesheetforthetimeoff%s.Ifyoudon'twantatimesheet,youshould"
                    "leavetheinternalprojectandtaskempty.")%(holiday_status.name))


classHolidays(models.Model):
    _inherit="hr.leave"

    timesheet_ids=fields.One2many('account.analytic.line','holiday_id',string="AnalyticLines")

    def_validate_leave_request(self):
        """Timesheetwillbegeneratedonleavevalidationonlyifatimesheet_project_idanda
            timesheet_task_idaresetonthecorrespondingleavetype.Thegeneratedtimesheetwill
            beattachedtothisproject/task.
        """
        #createthetimesheetonthevacationproject
        forholidayinself.filtered(
                lambdarequest:request.holiday_type=='employee'and
                                request.holiday_status_id.timesheet_project_idand
                                request.holiday_status_id.timesheet_task_id):
            holiday._timesheet_create_lines()

        returnsuper(Holidays,self)._validate_leave_request()

    def_timesheet_create_lines(self):
        self.ensure_one()
        vals_list=[]
        work_hours_data=self.employee_id.list_work_time_per_day(
            self.date_from,
            self.date_to,
        )
        forindex,(day_date,work_hours_count)inenumerate(work_hours_data):
            vals_list.append(self._timesheet_prepare_line_values(index,work_hours_data,day_date,work_hours_count))
        timesheets=self.env['account.analytic.line'].sudo().create(vals_list)
        returntimesheets

    def_timesheet_prepare_line_values(self,index,work_hours_data,day_date,work_hours_count):
        self.ensure_one()
        return{
            'name':"%s(%s/%s)"%(self.holiday_status_id.nameor'',index+1,len(work_hours_data)),
            'project_id':self.holiday_status_id.timesheet_project_id.id,
            'task_id':self.holiday_status_id.timesheet_task_id.id,
            'account_id':self.holiday_status_id.timesheet_project_id.analytic_account_id.id,
            'unit_amount':work_hours_count,
            'user_id':self.employee_id.user_id.id,
            'date':day_date,
            'holiday_id':self.id,
            'employee_id':self.employee_id.id,
            'company_id':self.holiday_status_id.timesheet_task_id.company_id.idorself.holiday_status_id.timesheet_project_id.company_id.id,
        }

    defaction_refuse(self):
        """Removethetimesheetslinkedtotherefusedholidays"""
        result=super(Holidays,self).action_refuse()
        timesheets=self.sudo().mapped('timesheet_ids')
        timesheets.write({'holiday_id':False})
        timesheets.unlink()
        returnresult
