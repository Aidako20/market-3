#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,tools


classTimesheetAttendance(models.Model):
    _name='hr.timesheet.attendance.report'
    _auto=False
    _description='TimesheetAttendanceReport'

    user_id=fields.Many2one('res.users')
    date=fields.Date()
    total_timesheet=fields.Float()
    total_attendance=fields.Float()
    total_difference=fields.Float()

    definit(self):
        tools.drop_view_if_exists(self.env.cr,self._table)
        self._cr.execute("""CREATEORREPLACEVIEW%sAS(
            SELECT
                max(id)ASid,
                t.user_id,
                t.date,
                coalesce(sum(t.attendance),0)AStotal_attendance,
                coalesce(sum(t.timesheet),0)AStotal_timesheet,
                coalesce(sum(t.attendance),0)-coalesce(sum(t.timesheet),0)astotal_difference
            FROM(
                SELECT
                    -hr_attendance.idASid,
                    resource_resource.user_idASuser_id,
                    hr_attendance.worked_hoursASattendance,
                    NULLAStimesheet,
                    hr_attendance.check_in::dateASdate
                FROMhr_attendance
                LEFTJOINhr_employeeONhr_employee.id=hr_attendance.employee_id
                LEFTJOINresource_resourceonresource_resource.id=hr_employee.resource_id
            UNIONALL
                SELECT
                    ts.idASid,
                    ts.user_idASuser_id,
                    NULLASattendance,
                    ts.unit_amountAStimesheet,
                    ts.dateASdate
                FROMaccount_analytic_lineASts
                WHEREts.project_idISNOTNULL
            )ASt
            GROUPBYt.user_id,t.date
            ORDERBYt.date
        )
        """%self._table)
