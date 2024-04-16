#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_

fromflectra.tools.safe_evalimportsafe_eval
fromflectra.tools.sqlimportcolumn_exists,create_column


classSaleOrder(models.Model):
    _inherit='sale.order'

    tasks_ids=fields.Many2many('project.task',compute='_compute_tasks_ids',string='Tasksassociatedtothissale')
    tasks_count=fields.Integer(string='Tasks',compute='_compute_tasks_ids',groups="project.group_project_user")

    visible_project=fields.Boolean('Displayproject',compute='_compute_visible_project',readonly=True)
    project_id=fields.Many2one(
        'project.project','Project',readonly=True,states={'draft':[('readonly',False)],'sent':[('readonly',False)]},
        help='Selectanonbillableprojectonwhichtaskscanbecreated.')
    project_ids=fields.Many2many('project.project',compute="_compute_project_ids",string='Projects',copy=False,groups="project.group_project_manager",help="Projectsusedinthissalesorder.")

    @api.depends('order_line.product_id.project_id')
    def_compute_tasks_ids(self):
        fororderinself:
            order.tasks_ids=self.env['project.task'].search(['|',('sale_line_id','in',order.order_line.ids),('sale_order_id','=',order.id)])
            order.tasks_count=len(order.tasks_ids)

    @api.depends('order_line.product_id.service_tracking')
    def_compute_visible_project(self):
        """Usersshouldbeabletoselectaproject_idontheSOifatleastoneSOlinehasaproductwithitsservicetracking
        configuredas'task_in_project'"""
        fororderinself:
            order.visible_project=any(
                service_tracking=='task_in_project'forservice_trackinginorder.order_line.mapped('product_id.service_tracking')
            )

    @api.depends('order_line.product_id','order_line.project_id')
    def_compute_project_ids(self):
        fororderinself:
            projects=order.order_line.mapped('product_id.project_id')
            projects|=order.order_line.mapped('project_id')
            projects|=order.project_id
            order.project_ids=projects

    @api.onchange('project_id')
    def_onchange_project_id(self):
        """SettheSOanalyticaccounttotheselectedproject'sanalyticaccount"""
        ifself.project_id.analytic_account_id:
            self.analytic_account_id=self.project_id.analytic_account_id

    def_action_confirm(self):
        """OnSOconfirmation,somelinesshouldgenerateataskoraproject."""
        result=super()._action_confirm()
        iflen(self.company_id)==1:
            #Allordersareinthesamecompany
            self.order_line.sudo().with_company(self.company_id)._timesheet_service_generation()
        else:
            #Ordersfromdifferentcompaniesareconfirmedtogether
            fororderinself:
                order.order_line.sudo().with_company(order.company_id)._timesheet_service_generation()
        returnresult

    defaction_view_task(self):
        self.ensure_one()

        list_view_id=self.env.ref('project.view_task_tree2').id
        form_view_id=self.env.ref('project.view_task_form2').id

        action={'type':'ir.actions.act_window_close'}
        task_projects=self.tasks_ids.mapped('project_id')
        iflen(task_projects)==1andlen(self.tasks_ids)>1: #redirecttotaskoftheproject(withkanbanstage,...)
            action=self.with_context(active_id=task_projects.id).env['ir.actions.actions']._for_xml_id(
                'project.act_project_project_2_project_task_all')
            action['domain']=[('id','in',self.tasks_ids.ids)]
            ifaction.get('context'):
                eval_context=self.env['ir.actions.actions']._get_eval_context()
                eval_context.update({'active_id':task_projects.id})
                action_context=safe_eval(action['context'],eval_context)
                action_context.update(eval_context)
                action['context']=action_context
        else:
            action=self.env["ir.actions.actions"]._for_xml_id("project.action_view_task")
            action['context']={} #erasedefaultcontexttoavoiddefaultfilter
            iflen(self.tasks_ids)>1: #crossprojectkanbantask
                action['views']=[[False,'kanban'],[list_view_id,'tree'],[form_view_id,'form'],[False,'graph'],[False,'calendar'],[False,'pivot']]
            eliflen(self.tasks_ids)==1: #singletask->formview
                action['views']=[(form_view_id,'form')]
                action['res_id']=self.tasks_ids.id
        #filteronthetaskofthecurrentSO
        action.setdefault('context',{})
        action['context'].update({'search_default_sale_order_id':self.id})
        returnaction

    defaction_view_project_ids(self):
        self.ensure_one()
        view_form_id=self.env.ref('project.edit_project').id
        view_kanban_id=self.env.ref('project.view_project_kanban').id
        action={
            'type':'ir.actions.act_window',
            'domain':[('id','in',self.project_ids.ids)],
            'views':[(view_kanban_id,'kanban'),(view_form_id,'form')],
            'view_mode':'kanban,form',
            'name':_('Projects'),
            'res_model':'project.project',
        }
        returnaction

    defwrite(self,values):
        if'state'invaluesandvalues['state']=='cancel':
            self.project_id.sudo().sale_line_id=False
        returnsuper(SaleOrder,self).write(values)


classSaleOrderLine(models.Model):
    _inherit="sale.order.line"

    project_id=fields.Many2one(
        'project.project','GeneratedProject',
        index=True,copy=False,help="Projectgeneratedbythesalesorderitem")
    task_id=fields.Many2one(
        'project.task','GeneratedTask',
        index=True,copy=False,help="Taskgeneratedbythesalesorderitem")
    is_service=fields.Boolean("IsaService",compute='_compute_is_service',store=True,compute_sudo=True,help="SalesOrderitemshouldgenerateataskand/oraproject,dependingontheproductsettings.")

    @api.depends('product_id.type')
    def_compute_is_service(self):
        forso_lineinself:
            so_line.is_service=so_line.product_id.type=='service'

    @api.depends('product_id.type')
    def_compute_product_updatable(self):
        forlineinself:
            ifline.product_id.type=='service'andline.state=='sale':
                line.product_updatable=False
            else:
                super(SaleOrderLine,line)._compute_product_updatable()

    def_auto_init(self):
        """
        CreatecolumntostopORMfromcomputingithimself(tooslow)
        """
        ifnotcolumn_exists(self.env.cr,'sale_order_line','is_service'):
            create_column(self.env.cr,'sale_order_line','is_service','bool')
            self.env.cr.execute("""
                UPDATEsale_order_lineline
                SETis_service=(pt.type='service')
                FROMproduct_productpp
                LEFTJOINproduct_templateptONpt.id=pp.product_tmpl_id
                WHEREpp.id=line.product_id
            """)
        returnsuper()._auto_init()

    @api.model_create_multi
    defcreate(self,vals_list):
        lines=super().create(vals_list)
        #Donotgeneratetask/projectwhenexpenseSOline,butallow
        #generatetaskwithhours=0.
        forlineinlines:
            ifline.state=='sale'andnotline.is_expense:
                line.sudo()._timesheet_service_generation()
                #iftheSOlinecreatedatask,postamessageontheorder
                ifline.task_id:
                    msg_body=_("TaskCreated(%s):<ahref=#data-oe-model=project.taskdata-oe-id=%d>%s</a>")%(line.product_id.name,line.task_id.id,line.task_id.name)
                    line.order_id.message_post(body=msg_body)
        returnlines

    defwrite(self,values):
        result=super().write(values)
        #changingtheorderedquantityshouldchangetheplannedhoursonthe
        #task,whatevertheSOstate.Itwillbeblockedbythesuperincase
        #ofalockedsaleorder.
        if'product_uom_qty'invaluesandnotself.env.context.get('no_update_planned_hours',False):
            forlineinself:
                ifline.task_idandline.product_id.type=='service':
                    planned_hours=line._convert_qty_company_hours(line.task_id.company_id)
                    line.task_id.write({'planned_hours':planned_hours})
        returnresult

    ###########################################
    #Service:Projectandtaskgeneration
    ###########################################

    def_convert_qty_company_hours(self,dest_company):
        returnself.product_uom_qty

    def_timesheet_create_project_prepare_values(self):
        """Generateprojectvalues"""
        account=self.order_id.analytic_account_id
        ifnotaccount:
            self.order_id._create_analytic_account(prefix=self.product_id.default_codeorNone)
            account=self.order_id.analytic_account_id

        #createtheprojectorduplicateone
        return{
            'name':'%s-%s'%(self.order_id.client_order_ref,self.order_id.name)ifself.order_id.client_order_refelseself.order_id.name,
            'analytic_account_id':account.id,
            'partner_id':self.order_id.partner_id.id,
            'sale_line_id':self.id,
            'sale_order_id':self.order_id.id,
            'active':True,
            'company_id':self.company_id.id,
        }

    def_timesheet_create_project(self):
        """Generateprojectforthegivensoline,andlinkit.
            :paramproject:recordofproject.projectinwhichthetaskshouldbecreated
            :returntask:recordofthecreatedtask
        """
        self.ensure_one()
        values=self._timesheet_create_project_prepare_values()
        ifself.product_id.project_template_id:
            values['name']="%s-%s"%(values['name'],self.product_id.project_template_id.name)
            project=self.product_id.project_template_id.copy(values)
            project.tasks.write({
                'sale_line_id':self.id,
                'partner_id':self.order_id.partner_id.id,
                'email_from':self.order_id.partner_id.email,
            })
            #duplicatingaprojectdoesn'tsettheSOonsub-tasks
            project.tasks.filtered(lambdatask:task.parent_id!=False).write({
                'sale_line_id':self.id,
                'sale_order_id':self.order_id,
            })
        else:
            project=self.env['project.project'].create(values)

        #Avoidnewtaskstogoto'UndefinedStage'
        ifnotproject.type_ids:
            project.type_ids=self.env['project.task.type'].create({'name':_('New')})

        #linkprojectasgeneratedbycurrentsoline
        self.write({'project_id':project.id})
        returnproject

    def_timesheet_create_task_prepare_values(self,project):
        self.ensure_one()
        planned_hours=self._convert_qty_company_hours(self.company_id)
        sale_line_name_parts=self.name.split('\n')
        title=sale_line_name_parts[0]orself.product_id.name
        description='<br/>'.join(sale_line_name_parts[1:])
        return{
            'name':titleifproject.sale_line_idelse'%s:%s'%(self.order_id.nameor'',title),
            'planned_hours':planned_hours,
            'partner_id':self.order_id.partner_id.id,
            'email_from':self.order_id.partner_id.email,
            'description':description,
            'project_id':project.id,
            'sale_line_id':self.id,
            'sale_order_id':self.order_id.id,
            'company_id':project.company_id.id,
            'user_id':False, #forcenonassignedtask,ascreatedassudo()
        }

    def_timesheet_create_task(self,project):
        """Generatetaskforthegivensoline,andlinkit.
            :paramproject:recordofproject.projectinwhichthetaskshouldbecreated
            :returntask:recordofthecreatedtask
        """
        values=self._timesheet_create_task_prepare_values(project)
        task=self.env['project.task'].sudo().create(values)
        self.write({'task_id':task.id})
        #postmessageontask
        task_msg=_("Thistaskhasbeencreatedfrom:<ahref=#data-oe-model=sale.orderdata-oe-id=%d>%s</a>(%s)")%(self.order_id.id,self.order_id.name,self.product_id.name)
        task.message_post(body=task_msg)
        returntask

    def_timesheet_service_generation(self):
        """Forservicelines,createthetaskortheproject.Ifalreadyexists,itsimplylinks
            theexistingonetotheline.
            Note:IftheSOwasconfirmed,cancelled,settodraftthenconfirmed,avoidcreatinga
            newproject/task.Thisexplainsthesearcheson'sale_line_id'onproject/task.Thisalso
            impliedifsolineofgeneratedtaskhasbeenmodified,wemayregenerateit.
        """
        so_line_task_global_project=self.filtered(lambdasol:sol.is_serviceandsol.product_id.service_tracking=='task_global_project')
        so_line_new_project=self.filtered(lambdasol:sol.is_serviceandsol.product_id.service_trackingin['project_only','task_in_project'])

        #searchsolinesfromSOofcurrentsolineshavingtheirprojectgenerated,inordertocheckifthecurrentonecan
        #createitsownproject,orreusetheoneofitsorder.
        map_so_project={}
        ifso_line_new_project:
            order_ids=self.mapped('order_id').ids
            so_lines_with_project=self.search([('order_id','in',order_ids),('project_id','!=',False),('product_id.service_tracking','in',['project_only','task_in_project']),('product_id.project_template_id','=',False)])
            map_so_project={sol.order_id.id:sol.project_idforsolinso_lines_with_project}
            so_lines_with_project_templates=self.search([('order_id','in',order_ids),('project_id','!=',False),('product_id.service_tracking','in',['project_only','task_in_project']),('product_id.project_template_id','!=',False)])
            map_so_project_templates={(sol.order_id.id,sol.product_id.project_template_id.id):sol.project_idforsolinso_lines_with_project_templates}

        #searchtheglobalprojectofcurrentSOlines,inwhichcreatetheirtask
        map_sol_project={}
        ifso_line_task_global_project:
            map_sol_project={sol.id:sol.product_id.with_company(sol.company_id).project_idforsolinso_line_task_global_project}

        def_can_create_project(sol):
            ifnotsol.project_id:
                ifsol.product_id.project_template_id:
                    return(sol.order_id.id,sol.product_id.project_template_id.id)notinmap_so_project_templates
                elifsol.order_id.idnotinmap_so_project:
                    returnTrue
            returnFalse

        def_determine_project(so_line):
            """Determinetheprojectforthissaleorderline.
            Rulesaredifferentbasedontheservice_tracking:

            -'project_only':theproject_idcanonlycomefromthesaleorderlineitself
            -'task_in_project':theproject_idcomesfromthesaleorderlineonlyifnoproject_idwasconfigured
              ontheparentsaleorder"""

            ifso_line.product_id.service_tracking=='project_only':
                returnso_line.project_id
            elifso_line.product_id.service_tracking=='task_in_project':
                returnso_line.order_id.project_idorso_line.project_id

            returnFalse

        #task_global_project:createtaskinglobalproject
        forso_lineinso_line_task_global_project:
            ifnotso_line.task_id:
                ifmap_sol_project.get(so_line.id):
                    so_line._timesheet_create_task(project=map_sol_project[so_line.id])

        #project_only,task_in_project:createanewproject,basedornotonatemplate(1perSO).Maybecreateatasktoo.
        #if'task_in_project'andproject_idconfiguredonSO,usethatoneinstead
        forso_lineinso_line_new_project:
            project=_determine_project(so_line)
            ifnotprojectand_can_create_project(so_line):
                project=so_line._timesheet_create_project()
                ifso_line.product_id.project_template_id:
                    map_so_project_templates[(so_line.order_id.id,so_line.product_id.project_template_id.id)]=project
                else:
                    map_so_project[so_line.order_id.id]=project
            elifnotproject:
                #AttachsubsequentSOlinestothecreatedproject
                so_line.project_id=(
                    map_so_project_templates.get((so_line.order_id.id,so_line.product_id.project_template_id.id))
                    ormap_so_project.get(so_line.order_id.id)
                )
            ifso_line.product_id.service_tracking=='task_in_project':
                ifnotproject:
                    ifso_line.product_id.project_template_id:
                        project=map_so_project_templates[(so_line.order_id.id,so_line.product_id.project_template_id.id)]
                    else:
                        project=map_so_project[so_line.order_id.id]
                ifnotso_line.task_id:
                    so_line._timesheet_create_task(project=project)
