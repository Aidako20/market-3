#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models
fromflectra.tools.translateimport_
fromdatetimeimporttimedelta


classHrEmployee(models.Model):
    _inherit="hr.employee"

    newly_hired_employee=fields.Boolean('Newlyhiredemployee',compute='_compute_newly_hired_employee',
                                          search='_search_newly_hired_employee')
    applicant_id=fields.One2many('hr.applicant','emp_id','Applicant')

    def_compute_newly_hired_employee(self):
        now=fields.Datetime.now()
        foremployeeinself:
            employee.newly_hired_employee=bool(employee.create_date>(now-timedelta(days=90)))

    def_search_newly_hired_employee(self,operator,value):
        employees=self.env['hr.employee'].search([
            ('create_date','>',fields.Datetime.now()-timedelta(days=90))
        ])
        return[('id','in',employees.ids)]

    @api.model
    defcreate(self,vals):
        new_employee=super(HrEmployee,self).create(vals)
        ifnew_employee.applicant_id:
            new_employee.applicant_id.message_post_with_view(
                        'hr_recruitment.applicant_hired_template',
                        values={'applicant':new_employee.applicant_id},
                        subtype_id=self.env.ref("hr_recruitment.mt_applicant_hired").id)
        returnnew_employee
