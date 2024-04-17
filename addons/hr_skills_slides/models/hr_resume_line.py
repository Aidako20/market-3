# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from flectra import fields, models


class ResumeLine(models.Model):
_inherit = 'hr.resume.line'

display_type = fields.Selection(selection_add=[('course', 'Course')])
channel_id = fields.Many2one('slide.channel', string="Course", readonly=True)
