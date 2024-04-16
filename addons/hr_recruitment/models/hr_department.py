#-*-coding:utf-8-*-

fromflectraimportapi,fields,models


classHrDepartment(models.Model):
    _inherit='hr.department'

    new_applicant_count=fields.Integer(
        compute='_compute_new_applicant_count',string='NewApplicant')
    new_hired_employee=fields.Integer(
        compute='_compute_recruitment_stats',string='NewHiredEmployee')
    expected_employee=fields.Integer(
        compute='_compute_recruitment_stats',string='ExpectedEmployee')

    def_compute_new_applicant_count(self):
        applicant_data=self.env['hr.applicant'].read_group(
            [('department_id','in',self.ids),('stage_id.sequence','<=','1')],
            ['department_id'],['department_id'])
        result=dict((data['department_id'][0],data['department_id_count'])fordatainapplicant_data)
        fordepartmentinself:
            department.new_applicant_count=result.get(department.id,0)

    def_compute_recruitment_stats(self):
        job_data=self.env['hr.job'].read_group(
            [('department_id','in',self.ids)],
            ['no_of_hired_employee','no_of_recruitment','department_id'],['department_id'])
        new_emp=dict((data['department_id'][0],data['no_of_hired_employee'])fordatainjob_data)
        expected_emp=dict((data['department_id'][0],data['no_of_recruitment'])fordatainjob_data)
        fordepartmentinself:
            department.new_hired_employee=new_emp.get(department.id,0)
            department.expected_employee=expected_emp.get(department.id,0)
