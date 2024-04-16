#-*-coding:utf-8-*-

fromflectraimportfields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    resource_calendar_id=fields.Many2one(
        'resource.calendar','CompanyWorkingHours',
        related='company_id.resource_calendar_id',readonly=False)
    module_hr_presence=fields.Boolean(string="AdvancedPresenceControl")
    module_hr_skills=fields.Boolean(string="SkillsManagement")
    hr_presence_control_login=fields.Boolean(string="Basedonuserstatusinsystem",config_parameter='hr.hr_presence_control_login')
    hr_presence_control_email=fields.Boolean(string="Basedonnumberofemailssent",config_parameter='hr_presence.hr_presence_control_email')
    hr_presence_control_ip=fields.Boolean(string="BasedonIPAddress",config_parameter='hr_presence.hr_presence_control_ip')
    module_hr_attendance=fields.Boolean(string="Basedonattendances")
    hr_presence_control_email_amount=fields.Integer(related="company_id.hr_presence_control_email_amount",readonly=False)
    hr_presence_control_ip_list=fields.Char(related="company_id.hr_presence_control_ip_list",readonly=False)
    hr_employee_self_edit=fields.Boolean(string="EmployeeEditing",config_parameter='hr.hr_employee_self_edit')
