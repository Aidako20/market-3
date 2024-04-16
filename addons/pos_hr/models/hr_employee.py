#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importhashlib

fromflectraimportapi,models,_
fromflectra.exceptionsimportUserError

classHrEmployee(models.Model):

    _inherit='hr.employee'

    defget_barcodes_and_pin_hashed(self):
        ifnotself.env.user.has_group('point_of_sale.group_pos_user'):
            return[]
        #Applyvisibilityfilters(recordrules)
        visible_emp_ids=self.search([('id','in',self.ids)])
        employees_data=self.sudo().search_read([('id','in',visible_emp_ids.ids)],['barcode','pin'])

        foreinemployees_data:
            e['barcode']=hashlib.sha1(e['barcode'].encode('utf8')).hexdigest()ife['barcode']elseFalse
            e['pin']=hashlib.sha1(e['pin'].encode('utf8')).hexdigest()ife['pin']elseFalse
        returnemployees_data

    defunlink(self):
        configs_with_employees=self.env['pos.config'].search([('module_pos_hr','=','True')]).filtered(lambdac:c.current_session_id)
        configs_with_all_employees=configs_with_employees.filtered(lambdac:notc.employee_ids)
        configs_with_specific_employees=configs_with_employees.filtered(lambdac:c.employee_ids&self)
        ifconfigs_with_all_employeesorconfigs_with_specific_employees:
            error_msg=_("YoucannotdeleteanemployeethatmaybeusedinanactivePoSsession,closethesession(s)first:\n")
            foremployeeinself:
                config_ids=configs_with_all_employees|configs_with_specific_employees.filtered(lambdac:employeeinc.employee_ids)
                ifconfig_ids:
                    error_msg+=_("Employee:%s-PoSConfig(s):%s\n")%(employee.name,','.join(config.nameforconfiginconfig_ids))

            raiseUserError(error_msg)
        returnsuper(HrEmployee,self).unlink()
