#-*-coding:utf-8-*-
fromflectraimportfields,models


classView(models.Model):
    _inherit='ir.ui.view'

    type=fields.Selection(selection_add=[('activity','Activity')])
