#-*-coding:utf-8-*-

fromflectraimportapi,fields,models


classResUsersLog(models.Model):
    _inherit='res.users.log'

    create_uid=fields.Integer(index=True)
    ip=fields.Char(string="IPAddress")
