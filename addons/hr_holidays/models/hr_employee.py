#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importdatetime
fromdateutil.relativedeltaimportrelativedelta

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError
fromflectra.tools.float_utilsimportfloat_round


classHrEmployeeBase(models.AbstractModel):
    _inherit="hr.employee.base"

    leave_manager_id=fields.Many2one(
        'res.users',string='TimeOff',
        compute='_compute_leave_manager',store=True,readonly=False,
        help='Selecttheuserresponsibleforapproving"TimeOff"ofthisemployee.\n'
             'Ifempty,theapprovalisdonebyanAdministratororApprover(determinedinsettings/users).')
    remaining_leaves=fields.Float(
        compute='_compute_remaining_leaves',string='RemainingPaidTimeOff',
        help='Totalnumberofpaidtimeoffallocatedtothisemployee,changethisvaluetocreateallocation/timeoffrequest.'
             'Totalbasedonallthetimeofftypeswithoutoverridinglimit.')
    current_leave_state=fields.Selection(compute='_compute_leave_status',string="CurrentTimeOffStatus",
        selection=[
            ('draft','New'),
            ('confirm','WaitingApproval'),
            ('refuse','Refused'),
            ('validate1','WaitingSecondApproval'),
            ('validate','Approved'),
            ('cancel','Cancelled')
        ])
    current_leave_id=fields.Many2one('hr.leave.type',compute='_compute_leave_status',string="CurrentTimeOffType")
    leave_date_from=fields.Date('FromDate',compute='_compute_leave_status')
    leave_date_to=fields.Date('ToDate',compute='_compute_leave_status')
    leaves_count=fields.Float('NumberofTimeOff',compute='_compute_remaining_leaves')
    allocation_count=fields.Float('Totalnumberofdaysallocated.',compute='_compute_allocation_count')
    allocation_used_count=fields.Float('Totalnumberofdaysoffused',compute='_compute_total_allocation_used')
    show_leaves=fields.Boolean('AbletoseeRemainingTimeOff',compute='_compute_show_leaves')
    is_absent=fields.Boolean('AbsentToday',compute='_compute_leave_status',search='_search_absent_employee')
    allocation_display=fields.Char(compute='_compute_allocation_count')
    allocation_used_display=fields.Char(compute='_compute_total_allocation_used')
    hr_icon_display=fields.Selection(selection_add=[('presence_holiday_absent','Onleave'),
                                                      ('presence_holiday_present','Presentbutonleave')])

    def_get_date_start_work(self):
        returnself.create_date

    def_get_remaining_leaves(self):
        """Helpertocomputetheremainingleavesforthecurrentemployees
            :returnsdictwherethekeyistheemployeeid,andthevalueistheremainleaves
        """
        self._cr.execute("""
            SELECT
                sum(h.number_of_days)ASdays,
                h.employee_id
            FROM
                (
                    SELECTholiday_status_id,number_of_days,
                        state,employee_id
                    FROMhr_leave_allocation
                    UNIONALL
                    SELECTholiday_status_id,(number_of_days*-1)asnumber_of_days,
                        state,employee_id
                    FROMhr_leave
                )h
                joinhr_leave_typesON(s.id=h.holiday_status_id)
            WHERE
                s.active=trueANDh.state='validate'AND
                (s.allocation_type='fixed'ORs.allocation_type='fixed_allocation')AND
                h.employee_idin%s
            GROUPBYh.employee_id""",(tuple(self.ids),))
        returndict((row['employee_id'],row['days'])forrowinself._cr.dictfetchall())

    def_compute_remaining_leaves(self):
        remaining={}
        ifself.ids:
            remaining=self._get_remaining_leaves()
        foremployeeinself:
            value=float_round(remaining.get(employee.id,0.0),precision_digits=2)
            employee.leaves_count=value
            employee.remaining_leaves=value

    def_compute_allocation_count(self):
        data=self.env['hr.leave.allocation'].read_group([
            ('employee_id','in',self.ids),
            ('holiday_status_id.active','=',True),
            ('state','=','validate'),
        ],['number_of_days:sum','employee_id'],['employee_id'])
        rg_results=dict((d['employee_id'][0],d['number_of_days'])fordindata)
        foremployeeinself:
            employee.allocation_count=float_round(rg_results.get(employee.id,0.0),precision_digits=2)
            employee.allocation_display="%g"%employee.allocation_count

    def_compute_total_allocation_used(self):
        foremployeeinself:
            employee.allocation_used_count=float_round(employee.allocation_count-employee.remaining_leaves,precision_digits=2)
            employee.allocation_used_display="%g"%employee.allocation_used_count

    def_compute_presence_state(self):
        super()._compute_presence_state()
        employees=self.filtered(lambdaemployee:employee.hr_presence_state!='present'andemployee.is_absent)
        employees.update({'hr_presence_state':'absent'})

    def_compute_presence_icon(self):
        super()._compute_presence_icon()
        employees_absent=self.filtered(lambdaemployee:
                                         employee.hr_icon_displaynotin['presence_present','presence_absent_active']
                                         andemployee.is_absent)
        employees_absent.update({'hr_icon_display':'presence_holiday_absent'})
        employees_present=self.filtered(lambdaemployee:
                                          employee.hr_icon_displayin['presence_present','presence_absent_active']
                                          andemployee.is_absent)
        employees_present.update({'hr_icon_display':'presence_holiday_present'})

    def_compute_leave_status(self):
        #UsedSUPERUSER_IDtoforcefullygetstatusofotheruser'sleave,tobypassrecordrule
        holidays=self.env['hr.leave'].sudo().search([
            ('employee_id','in',self.ids),
            ('date_from','<=',fields.Datetime.now()),
            ('date_to','>=',fields.Datetime.now()),
            ('state','=','validate'),
        ])
        leave_data={}
        forholidayinholidays:
            leave_data[holiday.employee_id.id]={}
            leave_data[holiday.employee_id.id]['leave_date_from']=holiday.date_from.date()
            leave_data[holiday.employee_id.id]['leave_date_to']=holiday.date_to.date()
            leave_data[holiday.employee_id.id]['current_leave_state']=holiday.state
            leave_data[holiday.employee_id.id]['current_leave_id']=holiday.holiday_status_id.id

        foremployeeinself:
            employee.leave_date_from=leave_data.get(employee.id,{}).get('leave_date_from')
            employee.leave_date_to=leave_data.get(employee.id,{}).get('leave_date_to')
            employee.current_leave_state=leave_data.get(employee.id,{}).get('current_leave_state')
            employee.current_leave_id=leave_data.get(employee.id,{}).get('current_leave_id')
            employee.is_absent=leave_data.get(employee.id)andleave_data.get(employee.id,{}).get('current_leave_state')in['validate']

    @api.depends('parent_id')
    def_compute_leave_manager(self):
        foremployeeinself:
            previous_manager=employee._origin.parent_id.user_id
            manager=employee.parent_id.user_id
            ifmanagerandemployee.leave_manager_id==previous_managerornotemployee.leave_manager_id:
                employee.leave_manager_id=manager
            elifnotemployee.leave_manager_id:
                employee.leave_manager_id=False

    def_compute_show_leaves(self):
        show_leaves=self.env['res.users'].has_group('hr_holidays.group_hr_holidays_user')
        foremployeeinself:
            ifshow_leavesoremployee.user_id==self.env.user:
                employee.show_leaves=True
            else:
                employee.show_leaves=False

    def_search_absent_employee(self,operator,value):
        ifoperatornotin('=','!=')ornotisinstance(value,bool):
            raiseUserError(_('Operationnotsupported'))
        #Thissearchisonlyusedforthe'AbsentToday'filterhowever
        #thisonlyreturnsemployeesthatareabsentrightnow.
        today_date=datetime.datetime.utcnow().date()
        today_start=fields.Datetime.to_string(today_date)
        today_end=fields.Datetime.to_string(today_date+relativedelta(hours=23,minutes=59,seconds=59))
        holidays=self.env['hr.leave'].sudo().search([
            ('employee_id','!=',False),
            ('state','=','validate1'),
            ('date_from','<=',today_end),
            ('date_to','>=',today_start),
        ])
        operator=['in','notin'][(operator=='=')!=value]
        return[('id',operator,holidays.mapped('employee_id').ids)]

    @api.model
    defcreate(self,values):
        if'parent_id'invalues:
            manager=self.env['hr.employee'].browse(values['parent_id']).user_id
            values['leave_manager_id']=values.get('leave_manager_id',manager.id)
        ifvalues.get('leave_manager_id',False):
            approver_group=self.env.ref('hr_holidays.group_hr_holidays_responsible',raise_if_not_found=False)
            ifapprover_group:
                approver_group.sudo().write({'users':[(4,values['leave_manager_id'])]})
        returnsuper(HrEmployeeBase,self).create(values)

    defwrite(self,values):
        if'parent_id'invalues:
            manager=self.env['hr.employee'].browse(values['parent_id']).user_id
            ifmanager:
                to_change=self.filtered(lambdae:e.leave_manager_id==e.parent_id.user_idornote.leave_manager_id)
                to_change.write({'leave_manager_id':values.get('leave_manager_id',manager.id)})

        old_managers=self.env['res.users']
        if'leave_manager_id'invalues:
            old_managers=self.mapped('leave_manager_id')
            ifvalues['leave_manager_id']:
                old_managers-=self.env['res.users'].browse(values['leave_manager_id'])
                approver_group=self.env.ref('hr_holidays.group_hr_holidays_responsible',raise_if_not_found=False)
                ifapprover_group:
                    approver_group.sudo().write({'users':[(4,values['leave_manager_id'])]})

        res=super(HrEmployeeBase,self).write(values)
        #removeusersfromtheResponsiblegroupiftheyarenolongerleavemanagers
        old_managers._clean_leave_responsible_users()

        if'parent_id'invaluesor'department_id'invalues:
            today_date=fields.Datetime.now()
            hr_vals={}
            ifvalues.get('parent_id')isnotNone:
                hr_vals['manager_id']=values['parent_id']
            ifvalues.get('department_id')isnotNone:
                hr_vals['department_id']=values['department_id']
            holidays=self.env['hr.leave'].sudo().search(['|',('state','in',['draft','confirm']),('date_from','>',today_date),('employee_id','in',self.ids)])
            holidays.write(hr_vals)
            allocations=self.env['hr.leave.allocation'].sudo().search([('state','in',['draft','confirm']),('employee_id','in',self.ids)])
            allocations.write(hr_vals)
        returnres

classHrEmployeePrivate(models.Model):
    _inherit='hr.employee'

classHrEmployeePublic(models.Model):
    _inherit='hr.employee.public'

    def_compute_leave_status(self):
        super()._compute_leave_status()
        self.current_leave_id=False
