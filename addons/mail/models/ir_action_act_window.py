#-*-coding:utf-8-*-
fromflectraimportfields,models


classActWindowView(models.Model):
    _inherit='ir.actions.act_window.view'

    view_mode=fields.Selection(selection_add=[
        ('activity','Activity')
    ],ondelete={'activity':'cascade'})
