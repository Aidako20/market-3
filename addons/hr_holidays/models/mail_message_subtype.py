#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging

fromflectraimportapi,models

_logger=logging.getLogger(__name__)


classMailMessageSubtype(models.Model):
    _inherit='mail.message.subtype'

    def_get_department_subtype(self):
        returnself.search([
            ('res_model','=','hr.department'),
            ('parent_id','=',self.id)])

    def_update_department_subtype(self):
        forsubtypeinself:
            department_subtype=subtype._get_department_subtype()
            ifdepartment_subtype:
                department_subtype.write({
                    'name':subtype.name,
                    'default':subtype.default,
                })
            else:
                department_subtype=self.create({
                    'name':subtype.name,
                    'res_model':'hr.department',
                    'default':subtype.defaultorFalse,
                    'parent_id':subtype.id,
                    'relation_field':'department_id',
                })
            returndepartment_subtype

    @api.model
    defcreate(self,vals):
        result=super(MailMessageSubtype,self).create(vals)
        ifresult.res_modelin['hr.leave','hr.leave.allocation']:
            result._update_department_subtype()
        returnresult

    defwrite(self,vals):
        result=super(MailMessageSubtype,self).write(vals)
        self.filtered(
            lambdasubtype:subtype.res_modelin['hr.leave','hr.leave.allocation']
        )._update_department_subtype()
        returnresult
