#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,_
fromflectra.exceptionsimportAccessError


classDigest(models.Model):
    _inherit='digest.digest'

    kpi_hr_recruitment_new_colleagues=fields.Boolean('Employees')
    kpi_hr_recruitment_new_colleagues_value=fields.Integer(compute='_compute_kpi_hr_recruitment_new_colleagues_value')

    def_compute_kpi_hr_recruitment_new_colleagues_value(self):
        ifnotself.env.user.has_group('hr_recruitment.group_hr_recruitment_user'):
            raiseAccessError(_("Donothaveaccess,skipthisdataforuser'sdigestemail"))
        forrecordinself:
            start,end,company=record._get_kpi_compute_parameters()
            new_colleagues=self.env['hr.employee'].search_count([
                ('create_date','>=',start),
                ('create_date','<',end),
                ('company_id','=',company.id)
            ])
            record.kpi_hr_recruitment_new_colleagues_value=new_colleagues

    def_compute_kpis_actions(self,company,user):
        res=super(Digest,self)._compute_kpis_actions(company,user)
        res['kpi_hr_recruitment_new_colleagues']='hr.open_view_employee_list_my&menu_id=%s'%self.env.ref('hr.menu_hr_root').id
        returnres
