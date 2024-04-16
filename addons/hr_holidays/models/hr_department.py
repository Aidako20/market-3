#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importdatetime
fromdateutil.relativedeltaimportrelativedelta

fromflectraimportapi,fields,models


classDepartment(models.Model):

    _inherit='hr.department'

    absence_of_today=fields.Integer(
        compute='_compute_leave_count',string='AbsencebyToday')
    leave_to_approve_count=fields.Integer(
        compute='_compute_leave_count',string='TimeOfftoApprove')
    allocation_to_approve_count=fields.Integer(
        compute='_compute_leave_count',string='AllocationtoApprove')
    total_employee=fields.Integer(
        compute='_compute_total_employee',string='TotalEmployee')

    def_compute_leave_count(self):
        Requests=self.env['hr.leave']
        Allocations=self.env['hr.leave.allocation']
        today_date=datetime.datetime.utcnow().date()
        today_start=fields.Datetime.to_string(today_date) #getthemidnightofthecurrentutcday
        today_end=fields.Datetime.to_string(today_date+relativedelta(hours=23,minutes=59,seconds=59))

        leave_data=Requests.read_group(
            [('department_id','in',self.ids),
             ('state','=','confirm')],
            ['department_id'],['department_id'])
        allocation_data=Allocations.read_group(
            [('department_id','in',self.ids),
             ('state','=','confirm')],
            ['department_id'],['department_id'])
        absence_data=Requests.read_group(
            [('department_id','in',self.ids),('state','notin',['cancel','refuse']),
             ('date_from','<=',today_end),('date_to','>=',today_start)],
            ['department_id'],['department_id'])

        res_leave=dict((data['department_id'][0],data['department_id_count'])fordatainleave_data)
        res_allocation=dict((data['department_id'][0],data['department_id_count'])fordatainallocation_data)
        res_absence=dict((data['department_id'][0],data['department_id_count'])fordatainabsence_data)

        fordepartmentinself:
            department.leave_to_approve_count=res_leave.get(department.id,0)
            department.allocation_to_approve_count=res_allocation.get(department.id,0)
            department.absence_of_today=res_absence.get(department.id,0)

    def_compute_total_employee(self):
        emp_data=self.env['hr.employee'].read_group([('department_id','in',self.ids)],['department_id'],['department_id'])
        result=dict((data['department_id'][0],data['department_id_count'])fordatainemp_data)
        fordepartmentinself:
            department.total_employee=result.get(department.id,0)
