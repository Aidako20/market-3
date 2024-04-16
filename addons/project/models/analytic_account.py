#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError


classAccountAnalyticAccount(models.Model):
    _inherit='account.analytic.account'
    _description='AnalyticAccount'

    project_ids=fields.One2many('project.project','analytic_account_id',string='Projects')
    project_count=fields.Integer("ProjectCount",compute='_compute_project_count')

    @api.depends('project_ids')
    def_compute_project_count(self):
        project_data=self.env['project.project'].read_group([('analytic_account_id','in',self.ids)],['analytic_account_id'],['analytic_account_id'])
        mapping={m['analytic_account_id'][0]:m['analytic_account_id_count']forminproject_data}
        foraccountinself:
            account.project_count=mapping.get(account.id,0)

    @api.constrains('company_id')
    def_check_company_id(self):
        forrecordinself:
            ifrecord.company_idandnotall(record.company_id==cforcinrecord.project_ids.mapped('company_id')):
                raiseUserError(_('Youcannotchangethecompanyofananalyticalaccountifitisrelatedtoaproject.'))

    defunlink(self):
        projects=self.env['project.project'].search([('analytic_account_id','in',self.ids)])
        has_tasks=self.env['project.task'].search_count([('project_id','in',projects.ids)])
        ifhas_tasks:
            raiseUserError(_('Pleaseremoveexistingtasksintheprojectlinkedtotheaccountsyouwanttodelete.'))
        returnsuper(AccountAnalyticAccount,self).unlink()

    defaction_view_projects(self):
        kanban_view_id=self.env.ref('project.view_project_kanban').id
        result={
            "type":"ir.actions.act_window",
            "res_model":"project.project",
            "views":[[kanban_view_id,"kanban"],[False,"form"]],
            "domain":[['analytic_account_id','=',self.id]],
            "context":{"create":False},
            "name":"Projects",
        }
        iflen(self.project_ids)==1:
            result['views']=[(False,"form")]
            result['res_id']=self.project_ids.id
        returnresult
