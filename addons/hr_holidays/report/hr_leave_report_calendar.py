#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,tools,SUPERUSER_ID

fromflectra.addons.base.models.res_partnerimport_tz_get


classLeaveReportCalendar(models.Model):
    _name="hr.leave.report.calendar"
    _description='TimeOffCalendar'
    _auto=False
    _order="start_datetimeDESC,employee_id"

    name=fields.Char(string='Name',readonly=True)
    start_datetime=fields.Datetime(string='From',readonly=True)
    stop_datetime=fields.Datetime(string='To',readonly=True)
    tz=fields.Selection(_tz_get,string="Timezone",readonly=True)
    duration=fields.Float(string='Duration',readonly=True,store=False)
    employee_id=fields.Many2one('hr.employee',readonly=True)
    company_id=fields.Many2one('res.company',readonly=True)
    state=fields.Selection([
        ('draft','ToSubmit'),
        ('cancel','Cancelled'), #YTIThisstateseemstobeunused.Toremove
        ('confirm','ToApprove'),
        ('refuse','Refused'),
        ('validate1','SecondApproval'),
        ('validate','Approved')
    ],readonly=True)

    definit(self):
        tools.drop_view_if_exists(self._cr,'hr_leave_report_calendar')
        self._cr.execute("""CREATEORREPLACEVIEWhr_leave_report_calendarAS
        (SELECT
            row_number()OVER()ASid,
            CONCAT(em.name,':',hl.duration_display)ASname,
            hl.date_fromASstart_datetime,
            hl.date_toASstop_datetime,
            hl.employee_idASemployee_id,
            hl.stateASstate,
            em.company_idAScompany_id,
            CASE
                WHENhl.holiday_type='employee'THENrr.tz
                ELSE%s
            ENDAStz
        FROMhr_leavehl
            LEFTJOINhr_employeeem
                ONem.id=hl.employee_id
            LEFTJOINresource_resourcerr
                ONrr.id=em.resource_id
        WHERE
            hl.stateIN('confirm','validate','validate1')
        ORDERBYid);
        """,[self.env.company.resource_calendar_id.tzorself.env.user.tzor'UTC'])

    def_read(self,fields):
        res=super()._read(fields)
        ifself.env.context.get('hide_employee_name')and'employee_id'inself.env.context.get('group_by',[]):
            name_field=self._fields['name']
            forrecordinself.with_user(SUPERUSER_ID):
                self.env.cache.set(record,name_field,record.name.split(':')[-1].strip())
        returnres

    @api.model
    defget_unusual_days(self,date_from,date_to=None):
        #Checkingthecalendardirectlyallowstonotgreyouttheleavestaken
        #bytheemployee
        returnself.env['hr.leave'].get_unusual_days(date_from,date_to=date_to)
