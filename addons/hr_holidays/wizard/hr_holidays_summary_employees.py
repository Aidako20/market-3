#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importtime

fromflectraimportapi,fields,models


classHolidaysSummaryEmployee(models.TransientModel):

    _name='hr.holidays.summary.employee'
    _description='HRTimeOffSummaryReportByEmployee'

    date_from=fields.Date(string='From',required=True,default=lambda*a:time.strftime('%Y-%m-01'))
    emp=fields.Many2many('hr.employee','summary_emp_rel','sum_id','emp_id',string='Employee(s)')
    holiday_type=fields.Selection([
        ('Approved','Approved'),
        ('Confirmed','Confirmed'),
        ('both','BothApprovedandConfirmed')
    ],string='SelectTimeOffType',required=True,default='Approved')

    defprint_report(self):
        self.ensure_one()
        [data]=self.read()
        data['emp']=self.env.context.get('active_ids',[])
        employees=self.env['hr.employee'].browse(data['emp'])
        datas={
            'ids':[],
            'model':'hr.employee',
            'form':data
        }
        returnself.env.ref('hr_holidays.action_report_holidayssummary').report_action(employees,data=datas)
