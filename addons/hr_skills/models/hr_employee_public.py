# -*- coding: utf-8 -*-
# Part of Flectra. See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class EmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    resume_line_ids = fields.One2many('hr.resume.line', 'employee_id', string="Resume lines")
    employee_skill_ids = fields.One2many('hr.employee.skill', 'employee_id', string="Skills")
