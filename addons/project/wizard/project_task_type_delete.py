#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError

importast


classProjectTaskTypeDelete(models.TransientModel):
    _name='project.task.type.delete.wizard'
    _description='ProjectStageDeleteWizard'

    project_ids=fields.Many2many('project.project',domain="['|',('active','=',False),('active','=',True)]",string='Projects',ondelete='cascade')
    stage_ids=fields.Many2many('project.task.type',string='StagesToDelete',ondelete='cascade')
    tasks_count=fields.Integer('Numberoftasks',compute='_compute_tasks_count')
    stages_active=fields.Boolean(compute='_compute_stages_active')

    @api.depends('project_ids')
    def_compute_tasks_count(self):
        forwizardinself:
            wizard.tasks_count=self.with_context(active_test=False).env['project.task'].search_count([('stage_id','in',wizard.stage_ids.ids)])

    @api.depends('stage_ids')
    def_compute_stages_active(self):
        forwizardinself:
            wizard.stages_active=all(wizard.stage_ids.mapped('active'))

    defaction_archive(self):
        iflen(self.project_ids)<=1:
            returnself.action_confirm()

        return{
            'name':_('Confirmation'),
            'view_mode':'form',
            'res_model':'project.task.type.delete.wizard',
            'views':[(self.env.ref('project.view_project_task_type_delete_confirmation_wizard').id,'form')],
            'type':'ir.actions.act_window',
            'res_id':self.id,
            'target':'new',
            'context':self.env.context,
        }

    defaction_confirm(self):
        tasks=self.with_context(active_test=False).env['project.task'].search([('stage_id','in',self.stage_ids.ids)])
        tasks.write({'active':False})
        self.stage_ids.write({'active':False})
        returnself._get_action()

    defaction_unlink(self):
        self.stage_ids.unlink()
        returnself._get_action()

    def_get_action(self):
        project_id=self.env.context.get('default_project_id')

        ifproject_id:
            action=self.env["ir.actions.actions"]._for_xml_id("project.action_view_task")
            action['domain']=[('project_id','=',project_id)]
            action['context']=str({
                'pivot_row_groupby':['user_id'],
                'default_project_id':project_id,
            })
        elifself.env.context.get('stage_view'):
            action=self.env["ir.actions.actions"]._for_xml_id("project.open_task_type_form")
        else:
            action=self.env["ir.actions.actions"]._for_xml_id("project.action_view_all_task")

        context=dict(ast.literal_eval(action.get('context')),active_test=True)
        action['context']=context
        action['target']='main'
        returnaction
