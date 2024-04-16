#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api,exceptions,_
fromflectra.toolsimportformat_datetime


classHrAttendance(models.Model):
    _name="hr.attendance"
    _description="Attendance"
    _order="check_indesc"

    def_default_employee(self):
        returnself.env.user.employee_id

    employee_id=fields.Many2one('hr.employee',string="Employee",default=_default_employee,required=True,ondelete='cascade',index=True)
    department_id=fields.Many2one('hr.department',string="Department",related="employee_id.department_id",
        readonly=True)
    check_in=fields.Datetime(string="CheckIn",default=fields.Datetime.now,required=True)
    check_out=fields.Datetime(string="CheckOut")
    worked_hours=fields.Float(string='WorkedHours',compute='_compute_worked_hours',store=True,readonly=True)

    defname_get(self):
        result=[]
        forattendanceinself:
            ifnotattendance.check_out:
                result.append((attendance.id,_("%(empl_name)sfrom%(check_in)s")%{
                    'empl_name':attendance.employee_id.name,
                    'check_in':format_datetime(self.env,attendance.check_in,dt_format=False),
                }))
            else:
                result.append((attendance.id,_("%(empl_name)sfrom%(check_in)sto%(check_out)s")%{
                    'empl_name':attendance.employee_id.name,
                    'check_in':format_datetime(self.env,attendance.check_in,dt_format=False),
                    'check_out':format_datetime(self.env,attendance.check_out,dt_format=False),
                }))
        returnresult

    @api.depends('check_in','check_out')
    def_compute_worked_hours(self):
        forattendanceinself:
            ifattendance.check_outandattendance.check_in:
                delta=attendance.check_out-attendance.check_in
                attendance.worked_hours=delta.total_seconds()/3600.0
            else:
                attendance.worked_hours=False

    @api.constrains('check_in','check_out')
    def_check_validity_check_in_check_out(self):
        """verifiesifcheck_inisearlierthancheck_out."""
        forattendanceinself:
            ifattendance.check_inandattendance.check_out:
                ifattendance.check_out<attendance.check_in:
                    raiseexceptions.ValidationError(_('"CheckOut"timecannotbeearlierthan"CheckIn"time.'))

    @api.constrains('check_in','check_out','employee_id')
    def_check_validity(self):
        """Verifiesthevalidityoftheattendancerecordcomparedtotheothersfromthesameemployee.
            Forthesameemployeewemusthave:
                *maximum1"open"attendancerecord(withoutcheck_out)
                *nooverlappingtimesliceswithpreviousemployeerecords
        """
        forattendanceinself:
            #wetakethelatestattendancebeforeourcheck_intimeandcheckitdoesn'toverlapwithours
            last_attendance_before_check_in=self.env['hr.attendance'].search([
                ('employee_id','=',attendance.employee_id.id),
                ('check_in','<=',attendance.check_in),
                ('id','!=',attendance.id),
            ],order='check_indesc',limit=1)
            iflast_attendance_before_check_inandlast_attendance_before_check_in.check_outandlast_attendance_before_check_in.check_out>attendance.check_in:
                raiseexceptions.ValidationError(_("Cannotcreatenewattendancerecordfor%(empl_name)s,theemployeewasalreadycheckedinon%(datetime)s")%{
                    'empl_name':attendance.employee_id.name,
                    'datetime':format_datetime(self.env,attendance.check_in,dt_format=False),
                })

            ifnotattendance.check_out:
                #ifourattendanceis"open"(nocheck_out),weverifythereisnoother"open"attendance
                no_check_out_attendances=self.env['hr.attendance'].search([
                    ('employee_id','=',attendance.employee_id.id),
                    ('check_out','=',False),
                    ('id','!=',attendance.id),
                ],order='check_indesc',limit=1)
                ifno_check_out_attendances:
                    raiseexceptions.ValidationError(_("Cannotcreatenewattendancerecordfor%(empl_name)s,theemployeehasn'tcheckedoutsince%(datetime)s")%{
                        'empl_name':attendance.employee_id.name,
                        'datetime':format_datetime(self.env,no_check_out_attendances.check_in,dt_format=False),
                    })
            else:
                #weverifythatthelatestattendancewithcheck_intimebeforeourcheck_outtime
                #isthesameastheonebeforeourcheck_intimecomputedbefore,otherwiseitoverlaps
                last_attendance_before_check_out=self.env['hr.attendance'].search([
                    ('employee_id','=',attendance.employee_id.id),
                    ('check_in','<',attendance.check_out),
                    ('id','!=',attendance.id),
                ],order='check_indesc',limit=1)
                iflast_attendance_before_check_outandlast_attendance_before_check_in!=last_attendance_before_check_out:
                    raiseexceptions.ValidationError(_("Cannotcreatenewattendancerecordfor%(empl_name)s,theemployeewasalreadycheckedinon%(datetime)s")%{
                        'empl_name':attendance.employee_id.name,
                        'datetime':format_datetime(self.env,last_attendance_before_check_out.check_in,dt_format=False),
                    })

    @api.returns('self',lambdavalue:value.id)
    defcopy(self):
        raiseexceptions.UserError(_('Youcannotduplicateanattendance.'))
