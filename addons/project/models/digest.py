#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,_
fromflectra.exceptionsimportAccessError


classDigest(models.Model):
    _inherit='digest.digest'

    kpi_project_task_opened=fields.Boolean('OpenTasks')
    kpi_project_task_opened_value=fields.Integer(compute='_compute_project_task_opened_value')

    def_compute_project_task_opened_value(self):
        ifnotself.env.user.has_group('project.group_project_user'):
            raiseAccessError(_("Donothaveaccess,skipthisdataforuser'sdigestemail"))
        forrecordinself:
            start,end,company=record._get_kpi_compute_parameters()
            record.kpi_project_task_opened_value=self.env['project.task'].search_count([
                ('stage_id.fold','=',False),
                ('create_date','>=',start),
                ('create_date','<',end),
                ('company_id','=',company.id)
            ])

    def_compute_kpis_actions(self,company,user):
        res=super(Digest,self)._compute_kpis_actions(company,user)
        res['kpi_project_task_opened']='project.open_view_project_all&menu_id=%s'%self.env.ref('project.menu_main_pm').id
        returnres
