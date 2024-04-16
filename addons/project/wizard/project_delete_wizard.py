#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classProjectDelete(models.TransientModel):
    _name='project.delete.wizard'
    _description='ProjectDeleteWizard'

    project_ids=fields.Many2many('project.project',string='Projects')
    task_count=fields.Integer(compute='_compute_task_count')
    projects_archived=fields.Boolean(compute='_compute_projects_archived')

    def_compute_projects_archived(self):
        forwizardinself.with_context(active_test=False):
            wizard.projects_archived=all(notp.activeforpinwizard.project_ids)

    def_compute_task_count(self):
        forwizardinself:
            wizard.task_count=sum(wizard.with_context(active_test=False).project_ids.mapped('task_count'))

    defaction_archive(self):
        self.project_ids.write({'active':False})

    defconfirm_delete(self):
        self.with_context(active_test=False).project_ids.unlink()
        returnself.env["ir.actions.actions"]._for_xml_id("project.open_view_project_all_config")
