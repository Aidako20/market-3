#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromastimportliteral_eval

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError


classProject(models.Model):
    _inherit='project.project'

    sale_line_id=fields.Many2one(
        'sale.order.line','SalesOrderItem',copy=False,
        domain="[('is_service','=',True),('is_expense','=',False),('order_id','=',sale_order_id),('state','in',['sale','done']),'|',('company_id','=',False),('company_id','=',company_id)]",
        help="Salesorderitemtowhichtheprojectislinked.Linkthetimesheetentrytothesalesorderitemdefinedontheproject."
        "Onlyappliesontaskswithoutsaleorderitemdefined,andiftheemployeeisnotinthe'Employee/SalesOrderItemMapping'oftheproject.")
    sale_order_id=fields.Many2one('sale.order','SalesOrder',
        domain="[('order_line.product_id.type','=','service'),('partner_id','=',partner_id),('state','in',['sale','done'])]",
        copy=False,help="Salesordertowhichtheprojectislinked.")

    _sql_constraints=[
        ('sale_order_required_if_sale_line',"CHECK((sale_line_idISNOTNULLANDsale_order_idISNOTNULL)OR(sale_line_idISNULL))",'Theprojectshouldbelinkedtoasaleordertoselectasaleorderitem.'),
    ]

    @api.model
    def_map_tasks_default_valeus(self,task,project):
        defaults=super()._map_tasks_default_valeus(task,project)
        defaults['sale_line_id']=False
        returndefaults

    defaction_view_so(self):
        self.ensure_one()
        action_window={
            "type":"ir.actions.act_window",
            "res_model":"sale.order",
            "name":"SalesOrder",
            "views":[[False,"form"]],
            "context":{"create":False,"show_sale":True},
            "res_id":self.sale_order_id.id
        }
        returnaction_window


classProjectTask(models.Model):
    _inherit="project.task"

    sale_order_id=fields.Many2one('sale.order','SalesOrder',help="Salesordertowhichthetaskislinked.")
    sale_line_id=fields.Many2one(
        'sale.order.line','SalesOrderItem',domain="[('company_id','=',company_id),('is_service','=',True),('order_partner_id','child_of',commercial_partner_id),('is_expense','=',False),('state','in',['sale','done']),('order_id','=?',project_sale_order_id)]",
        compute='_compute_sale_line',store=True,readonly=False,copy=False,
        help="Salesorderitemtowhichtheprojectislinked.Linkthetimesheetentrytothesalesorderitemdefinedontheproject."
        "Onlyappliesontaskswithoutsaleorderitemdefined,andiftheemployeeisnotinthe'Employee/SalesOrderItemMapping'oftheproject.")
    project_sale_order_id=fields.Many2one('sale.order',string="Project'ssaleorder",related='project_id.sale_order_id')
    invoice_count=fields.Integer("Numberofinvoices",related='sale_order_id.invoice_count')
    task_to_invoice=fields.Boolean("Toinvoice",compute='_compute_task_to_invoice',search='_search_task_to_invoice',groups='sales_team.group_sale_salesman_all_leads')

    @api.depends('project_id.sale_line_id.order_partner_id')
    def_compute_partner_id(self):
        fortaskinself:
            ifnottask.partner_id:
                task.partner_id=task.project_id.sale_line_id.order_partner_id
        super()._compute_partner_id()

    @api.depends('commercial_partner_id','sale_line_id.order_partner_id.commercial_partner_id','parent_id.sale_line_id','project_id.sale_line_id')
    def_compute_sale_line(self):
        fortaskinself:
            ifnottask.sale_line_id:
                task.sale_line_id=task.parent_id.sale_line_idortask.project_id.sale_line_id
            #checksale_line_idandcustomerarecoherent
            iftask.sale_line_id.order_partner_id.commercial_partner_id!=task.partner_id.commercial_partner_id:
                task.sale_line_id=False

    @api.constrains('sale_line_id')
    def_check_sale_line_type(self):
        fortaskinself.sudo():
            iftask.sale_line_id:
                ifnottask.sale_line_id.is_serviceortask.sale_line_id.is_expense:
                    raiseValidationError(_(
                        'Youcannotlinktheorderitem%(order_id)s-%(product_id)stothistaskbecauseitisare-invoicedexpense.',
                        order_id=task.sale_line_id.order_id.name,
                        product_id=task.sale_line_id.product_id.display_name,
                    ))

    defunlink(self):
        ifany(task.sale_line_idfortaskinself):
            raiseValidationError(_('Youhavetounlinkthetaskfromthesaleorderiteminordertodeleteit.'))
        returnsuper().unlink()

    #---------------------------------------------------
    #Actions
    #---------------------------------------------------

    def_get_action_view_so_ids(self):
        returnself.sale_order_id.ids

    defaction_view_so(self):
        self.ensure_one()
        so_ids=self._get_action_view_so_ids()
        action_window={
            "type":"ir.actions.act_window",
            "res_model":"sale.order",
            "name":"SalesOrder",
            "views":[[False,"tree"],[False,"form"]],
            "context":{"create":False,"show_sale":True},
            "domain":[["id","in",so_ids]],
        }
        iflen(so_ids)==1:
            action_window["views"]=[[False,"form"]]
            action_window["res_id"]=so_ids[0]

        returnaction_window

    defrating_get_partner_id(self):
        partner=self.partner_idorself.sale_line_id.order_id.partner_id
        ifpartner:
            returnpartner
        returnsuper().rating_get_partner_id()

    @api.depends('sale_order_id.invoice_status','sale_order_id.order_line')
    def_compute_task_to_invoice(self):
        fortaskinself:
            iftask.sale_order_id:
                task.task_to_invoice=bool(task.sale_order_id.invoice_statusnotin('no','invoiced'))
            else:
                task.task_to_invoice=False

    @api.model
    def_search_task_to_invoice(self,operator,value):
        query="""
            SELECTso.id
            FROMsale_orderso
            WHEREso.invoice_status!='invoiced'
                ANDso.invoice_status!='no'
        """
        operator_new='inselect'
        if(bool(operator=='=')^bool(value)):
            operator_new='notinselect'
        return[('sale_order_id',operator_new,(query,()))]

    defaction_create_invoice(self):
        #ensuretheSOexistsbeforeinvoicing,thenconfirmit
        so_to_confirm=self.filtered(
            lambdatask:task.sale_order_idandtask.sale_order_id.statein['draft','sent']
        ).mapped('sale_order_id')
        so_to_confirm.action_confirm()

        #redirectcreateinvoicewizard(oftheSalesOrder)
        action=self.env["ir.actions.actions"]._for_xml_id("sale.action_view_sale_advance_payment_inv")
        context=literal_eval(action.get('context',"{}"))
        context.update({
            'active_id':self.sale_order_id.idiflen(self)==1elseFalse,
            'active_ids':self.mapped('sale_order_id').ids,
            'default_company_id':self.company_id.id,
        })
        action['context']=context
        returnaction

classProjectTaskRecurrence(models.Model):
    _inherit='project.task.recurrence'

    def_new_task_values(self,task):
        values=super(ProjectTaskRecurrence,self)._new_task_values(task)
        task=self.sudo().task_ids[0]
        values['sale_line_id']=self._get_sale_line_id(task)
        returnvalues

    def_get_sale_line_id(self,task):
        returntask.sale_line_id.id
