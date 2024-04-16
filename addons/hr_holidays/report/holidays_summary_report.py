#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importcalendar

fromdatetimeimporttimedelta
fromdateutil.relativedeltaimportrelativedelta
fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError


classHrHolidaySummaryReport(models.AbstractModel):
    _name='report.hr_holidays.report_holidayssummary'
    _description='HolidaysSummaryReport'

    def_get_header_info(self,start_date,holiday_type):
        st_date=fields.Date.from_string(start_date)
        return{
            'start_date':fields.Date.to_string(st_date),
            'end_date':fields.Date.to_string(st_date+relativedelta(days=59)),
            'holiday_type':'ConfirmedandApproved'ifholiday_type=='both'elseholiday_type
        }

    def_date_is_day_off(self,date):
        returndate.weekday()in(calendar.SATURDAY,calendar.SUNDAY,)

    def_get_day(self,start_date):
        res=[]
        start_date=fields.Date.from_string(start_date)
        forxinrange(0,60):
            color='#ababab'ifself._date_is_day_off(start_date)else''
            res.append({'day_str':start_date.strftime('%a'),'day':start_date.day,'color':color})
            start_date=start_date+relativedelta(days=1)
        returnres

    def_get_months(self,start_date):
        #itworksforgetingmonthnamebetweentwodates.
        res=[]
        start_date=fields.Date.from_string(start_date)
        end_date=start_date+relativedelta(days=59)
        whilestart_date<=end_date:
            last_date=start_date+relativedelta(day=1,months=+1,days=-1)
            iflast_date>end_date:
                last_date=end_date
            month_days=(last_date-start_date).days+1
            res.append({'month_name':start_date.strftime('%B'),'days':month_days})
            start_date+=relativedelta(day=1,months=+1)
        returnres

    def_get_leaves_summary(self,start_date,empid,holiday_type):
        res=[]
        count=0
        start_date=fields.Date.from_string(start_date)
        end_date=start_date+relativedelta(days=59)
        forindexinrange(0,60):
            current=start_date+timedelta(index)
            res.append({'day':current.day,'color':''})
            ifself._date_is_day_off(current):
                res[index]['color']='#ababab'
        #countandgetleavesummarydetails.
        holiday_type=['confirm','validate']ifholiday_type=='both'else['confirm']ifholiday_type=='Confirmed'else['validate']
        holidays=self.env['hr.leave'].search([
            ('employee_id','=',empid),('state','in',holiday_type),
            ('date_from','<=',str(end_date)),
            ('date_to','>=',str(start_date))
        ])
        forholidayinholidays:
            #Convertdatetousertimezone,otherwisethereportwillnotbeconsistentwiththe
            #valuedisplayedintheinterface.
            date_from=fields.Datetime.from_string(holiday.date_from)
            date_from=fields.Datetime.context_timestamp(holiday,date_from).date()
            date_to=fields.Datetime.from_string(holiday.date_to)
            date_to=fields.Datetime.context_timestamp(holiday,date_to).date()
            forindexinrange(0,((date_to-date_from).days+1)):
                ifdate_from>=start_dateanddate_from<=end_date:
                    res[(date_from-start_date).days]['color']=holiday.holiday_status_id.color_name
                date_from+=timedelta(1)
            count+=holiday.number_of_days
        employee=self.env['hr.employee'].browse(empid)
        return{'emp':employee.name,'display':res,'sum':count}

    def_get_data_from_report(self,data):
        res=[]
        Employee=self.env['hr.employee']
        if'depts'indata:
            fordepartmentinself.env['hr.department'].browse(data['depts']):
                res.append({
                    'dept':department.name,
                    'data':[
                        self._get_leaves_summary(data['date_from'],emp.id,data['holiday_type'])
                        forempinEmployee.search([('department_id','=',department.id)])
                    ],
                    'color':self._get_day(data['date_from']),
                })
        elif'emp'indata:
            res.append({'data':[
                self._get_leaves_summary(data['date_from'],emp.id,data['holiday_type'])
                forempinEmployee.browse(data['emp'])
            ]})
        returnres

    def_get_holidays_status(self):
        res=[]
        forholidayinself.env['hr.leave.type'].search([]):
            res.append({'color':holiday.color_name,'name':holiday.name})
        returnres

    @api.model
    def_get_report_values(self,docids,data=None):
        ifnotdata.get('form'):
            raiseUserError(_("Formcontentismissing,thisreportcannotbeprinted."))

        holidays_report=self.env['ir.actions.report']._get_report_from_name('hr_holidays.report_holidayssummary')
        holidays=self.env['hr.leave'].browse(self.ids)
        return{
            'doc_ids':self.ids,
            'doc_model':holidays_report.model,
            'docs':holidays,
            'get_header_info':self._get_header_info(data['form']['date_from'],data['form']['holiday_type']),
            'get_day':self._get_day(data['form']['date_from']),
            'get_months':self._get_months(data['form']['date_from']),
            'get_data_from_report':self._get_data_from_report(data['form']),
            'get_holidays_status':self._get_holidays_status(),
        }
