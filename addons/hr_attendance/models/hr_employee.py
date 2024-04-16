#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importpytz
fromdatetimeimportdatetime
fromdateutil.relativedeltaimportrelativedelta

fromflectraimportmodels,fields,api,exceptions,_,SUPERUSER_ID


classHrEmployeeBase(models.AbstractModel):
    _inherit="hr.employee.base"

    attendance_ids=fields.One2many('hr.attendance','employee_id',help='listofattendancesfortheemployee')
    last_attendance_id=fields.Many2one('hr.attendance',compute='_compute_last_attendance_id',store=True)
    last_check_in=fields.Datetime(related='last_attendance_id.check_in',store=True)
    last_check_out=fields.Datetime(related='last_attendance_id.check_out',store=True)
    attendance_state=fields.Selection(string="AttendanceStatus",compute='_compute_attendance_state',selection=[('checked_out',"Checkedout"),('checked_in',"Checkedin")])
    hours_last_month=fields.Float(compute='_compute_hours_last_month')
    hours_today=fields.Float(compute='_compute_hours_today')
    hours_last_month_display=fields.Char(compute='_compute_hours_last_month')

    @api.depends('user_id.im_status','attendance_state')
    def_compute_presence_state(self):
        """
        Overridetoincludecheckin/checkoutinthepresencestate
        Attendancehasthesecondhighestpriorityafterlogin
        """
        super()._compute_presence_state()
        employees=self.filtered(lambdae:e.hr_presence_state!='present')
        employee_to_check_working=self.filtered(lambdae:e.attendance_state=='checked_out'
                                                            ande.hr_presence_state=='to_define')
        working_now_list=employee_to_check_working._get_employee_working_now()
        foremployeeinemployees:
            ifemployee.attendance_state=='checked_out'andemployee.hr_presence_state=='to_define'and\
                    employee.idnotinworking_now_list:
                employee.hr_presence_state='absent'
            elifemployee.attendance_state=='checked_in':
                employee.hr_presence_state='present'

    def_compute_hours_last_month(self):
        now=fields.Datetime.now()
        now_utc=pytz.utc.localize(now)
        foremployeeinself:
            tz=pytz.timezone(employee.tzor'UTC')
            now_tz=now_utc.astimezone(tz)
            start_tz=now_tz+relativedelta(months=-1,day=1,hour=0,minute=0,second=0,microsecond=0)
            start_naive=start_tz.astimezone(pytz.utc).replace(tzinfo=None)
            end_tz=now_tz+relativedelta(day=1,hour=0,minute=0,second=0,microsecond=0)
            end_naive=end_tz.astimezone(pytz.utc).replace(tzinfo=None)

            attendances=self.env['hr.attendance'].search([
                ('employee_id','=',employee.id),
                '&',
                ('check_in','<=',end_naive),
                ('check_out','>=',start_naive),
            ])

            hours=0
            forattendanceinattendances:
                check_in=max(attendance.check_in,start_naive)
                check_out=min(attendance.check_out,end_naive)
                hours+=(check_out-check_in).total_seconds()/3600.0

            employee.hours_last_month=round(hours,2)
            employee.hours_last_month_display="%g"%employee.hours_last_month

    def_compute_hours_today(self):
        now=fields.Datetime.now()
        now_utc=pytz.utc.localize(now)
        foremployeeinself:
            #startofdayintheemployee'stimezonemightbethepreviousdayinutc
            tz=pytz.timezone(employee.tz)
            now_tz=now_utc.astimezone(tz)
            start_tz=now_tz+relativedelta(hour=0,minute=0) #daystartintheemployee'stimezone
            start_naive=start_tz.astimezone(pytz.utc).replace(tzinfo=None)

            attendances=self.env['hr.attendance'].search([
                ('employee_id','=',employee.id),
                ('check_in','<=',now),
                '|',('check_out','>=',start_naive),('check_out','=',False),
            ])

            worked_hours=0
            forattendanceinattendances:
                delta=(attendance.check_outornow)-max(attendance.check_in,start_naive)
                worked_hours+=delta.total_seconds()/3600.0
            employee.hours_today=worked_hours

    @api.depends('attendance_ids')
    def_compute_last_attendance_id(self):
        foremployeeinself:
            employee.last_attendance_id=self.env['hr.attendance'].search([
                ('employee_id','=',employee.id),
            ],limit=1)

    @api.depends('last_attendance_id.check_in','last_attendance_id.check_out','last_attendance_id')
    def_compute_attendance_state(self):
        foremployeeinself:
            att=employee.last_attendance_id.sudo()
            employee.attendance_state=attandnotatt.check_outand'checked_in'or'checked_out'

    @api.model
    defattendance_scan(self,barcode):
        """ReceiveabarcodescannedfromtheKioskModeandchangetheattendancesofcorrespondingemployee.
            Returnseitheranactionorawarning.
        """
        employee=self.sudo().search([('barcode','=',barcode)],limit=1)
        ifemployee:
            returnemployee._attendance_action('hr_attendance.hr_attendance_action_kiosk_mode')
        return{'warning':_("NoemployeecorrespondingtoBadgeID'%(barcode)s.'")%{'barcode':barcode}}

    defattendance_manual(self,next_action,entered_pin=None):
        self.ensure_one()
        attendance_user_and_no_pin=self.user_has_groups(
            'hr_attendance.group_hr_attendance_user,'
            '!hr_attendance.group_hr_attendance_use_pin')
        can_check_without_pin=attendance_user_and_no_pinor(self.user_id==self.env.userandentered_pinisNone)
        ifcan_check_without_pinorentered_pinisnotNoneandentered_pin==self.sudo().pin:
            returnself._attendance_action(next_action)
        return{'warning':_('WrongPIN')}

    def_attendance_action(self,next_action):
        """Changestheattendanceoftheemployee.
            Returnsanactiontothecheckin/outmessage,
            next_actiondefineswhichmenuthecheckin/outmessageshouldreturnto.("MyAttendances"or"KioskMode")
        """
        self.ensure_one()
        employee=self.sudo()
        action_message=self.env["ir.actions.actions"]._for_xml_id("hr_attendance.hr_attendance_action_greeting_message")
        action_message['previous_attendance_change_date']=employee.last_attendance_idand(employee.last_attendance_id.check_outoremployee.last_attendance_id.check_in)orFalse
        action_message['employee_name']=employee.name
        action_message['barcode']=employee.barcode
        action_message['next_action']=next_action
        action_message['hours_today']=employee.hours_today

        ifemployee.user_id:
            modified_attendance=employee.with_user(employee.user_id)._attendance_action_change()
        else:
            modified_attendance=employee._attendance_action_change()
        action_message['attendance']=modified_attendance.read()[0]
        return{'action':action_message}

    def_attendance_action_change(self):
        """CheckIn/CheckOutaction
            CheckIn:createanewattendancerecord
            CheckOut:modifycheck_outfieldofappropriateattendancerecord
        """
        self.ensure_one()
        action_date=fields.Datetime.now()

        ifself.attendance_state!='checked_in':
            vals={
                'employee_id':self.id,
                'check_in':action_date,
            }
            returnself.env['hr.attendance'].create(vals)
        attendance=self.env['hr.attendance'].search([('employee_id','=',self.id),('check_out','=',False)],limit=1)
        ifattendance:
            attendance.check_out=action_date
        else:
            raiseexceptions.UserError(_('Cannotperformcheckouton%(empl_name)s,couldnotfindcorrespondingcheckin.'
                'Yourattendanceshaveprobablybeenmodifiedmanuallybyhumanresources.')%{'empl_name':self.sudo().name,})
        returnattendance

    @api.model
    defread_group(self,domain,fields,groupby,offset=0,limit=None,orderby=False,lazy=True):
        if'pin'ingroupbyor'pin'inself.env.context.get('group_by','')orself.env.context.get('no_group_by'):
            raiseexceptions.UserError(_('Suchgroupingisnotallowed.'))
        returnsuper(HrEmployeeBase,self).read_group(domain,fields,groupby,offset=offset,limit=limit,orderby=orderby,lazy=lazy)

    def_compute_presence_icon(self):
        res=super()._compute_presence_icon()
        #Allemployeemustchekinorcheckout.Everybodymusthaveanicon
        employee_to_define=self.filtered(lambdae:e.hr_icon_display=='presence_undetermined')
        employee_to_define.hr_icon_display='presence_to_define'
        returnres
