#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError


classProjectCreateSalesOrder(models.TransientModel):
    _name='project.create.sale.order'
    _description="CreateSOfromproject"

    @api.model
    defdefault_get(self,fields):
        result=super(ProjectCreateSalesOrder,self).default_get(fields)

        active_model=self._context.get('active_model')
        ifactive_model!='project.project':
            raiseUserError(_("Youcanonlyapplythisactionfromaproject."))

        active_id=self._context.get('active_id')
        if'project_id'infieldsandactive_id:
            project=self.env['project.project'].browse(active_id)
            ifproject.sale_order_id:
                raiseUserError(_("Theprojecthasalreadyasaleorder."))
            result['project_id']=active_id
            ifnotresult.get('partner_id',False):
                result['partner_id']=project.partner_id.id
            ifproject.bill_type=='customer_project'andnotresult.get('line_ids',False):
                ifproject.pricing_type=='employee_rate':
                    default_product=self.env.ref('sale_timesheet.time_product',False)
                    result['line_ids']=[
                        (0,0,{
                            'employee_id':e.employee_id.id,
                            'product_id':e.timesheet_product_id.idordefault_product.id,
                            'price_unit':e.price_unitife.timesheet_product_idelsedefault_product.lst_price
                        })foreinproject.sale_line_employee_ids]
                    employee_from_timesheet=project.task_ids.timesheet_ids.employee_id-project.sale_line_employee_ids.employee_id
                    result['line_ids']+=[
                        (0,0,{
                            'employee_id':e.id,
                            'product_id':default_product.id,
                            'price_unit':default_product.lst_price
                        })foreinemployee_from_timesheet]
                else:
                    result['line_ids']=[
                        (0,0,{
                            'product_id':p.id,
                            'price_unit':p.lst_price
                        })forpinproject.task_ids.timesheet_product_id]
        returnresult

    project_id=fields.Many2one('project.project',"Project",domain=[('sale_line_id','=',False)],help="Projectforwhichwearecreatingasalesorder",required=True)
    company_id=fields.Many2one(related='project_id.company_id')
    partner_id=fields.Many2one('res.partner',string="Customer",required=True,help="Customerofthesalesorder")
    commercial_partner_id=fields.Many2one(related='partner_id.commercial_partner_id')

    pricing_type=fields.Selection(related="project_id.pricing_type")
    link_selection=fields.Selection([('create','Createanewsalesorder'),('link','Linktoanexistingsalesorder')],required=True,default='create')
    sale_order_id=fields.Many2one(
        'sale.order',string="SalesOrder",
        domain="['|','|',('partner_id','=',partner_id),('partner_id','child_of',commercial_partner_id),('partner_id','parent_of',partner_id)]")

    line_ids=fields.One2many('project.create.sale.order.line','wizard_id',string='Lines')
    info_invoice=fields.Char(compute='_compute_info_invoice')

    @api.depends('sale_order_id','link_selection')
    def_compute_info_invoice(self):
        forlineinself:
            tasks=line.project_id.tasks.filtered(lambdat:nott.non_allow_billable)
            domain=self.env['sale.order.line']._timesheet_compute_delivered_quantity_domain()
            timesheet=self.env['account.analytic.line'].read_group(domain+[('task_id','in',tasks.ids),('so_line','=',False),('timesheet_invoice_id','=',False)],['unit_amount'],['task_id'])
            unit_amount=round(sum(t.get('unit_amount',0)fortintimesheet),2)iftimesheetelse0
            ifnotunit_amount:
                line.info_invoice=False
                continue
            company_uom=self.env.company.timesheet_encode_uom_id
            label=_("hours")
            ifcompany_uom==self.env.ref('uom.product_uom_day'):
                label=_("days")
            ifline.link_selection=='create':
                line.info_invoice=_("%(amount)s%(label)swillbeaddedtothenewSalesOrder.",amount=unit_amount,label=label)
            else:
                line.info_invoice=_("%(amount)s%(label)swillbeaddedtotheselectedSalesOrder.",amount=unit_amount,label=label)

    @api.onchange('partner_id')
    def_onchange_partner_id(self):
        self.sale_order_id=False

    defaction_link_sale_order(self):
        task_no_sale_line=self.project_id.tasks.filtered(lambdatask:nottask.sale_line_id)
        #linktheprojecttotheSOline
        self.project_id.write({
            'sale_line_id':self.sale_order_id.order_line[0].id,
            'sale_order_id':self.sale_order_id.id,
            'partner_id':self.partner_id.id,
        })

        ifself.pricing_type=='employee_rate':
            lines_already_present=dict([(l.employee_id.id,l)forlinself.project_id.sale_line_employee_ids])
            EmployeeMap=self.env['project.sale.line.employee.map'].sudo()

            forwizard_lineinself.line_ids:
                ifwizard_line.employee_id.idnotinlines_already_present:
                    EmployeeMap.create({
                        'project_id':self.project_id.id,
                        'sale_line_id':wizard_line.sale_line_id.id,
                        'employee_id':wizard_line.employee_id.id,
                    })
                else:
                    lines_already_present[wizard_line.employee_id.id].write({
                        'sale_line_id':wizard_line.sale_line_id.id
                    })

            self.project_id.tasks.filtered(lambdatask:task.non_allow_billable).sale_line_id=False
            tasks=self.project_id.tasks.filtered(lambdat:nott.non_allow_billable)
            #assignSOLtotimesheets
            formap_entryinself.project_id.sale_line_employee_ids:
                self.env['account.analytic.line'].search([('task_id','in',tasks.ids),('employee_id','=',map_entry.employee_id.id),('so_line','=',False)]).write({
                    'so_line':map_entry.sale_line_id.id
                })
        else:
            dict_product_sol=dict([(l.product_id.id,l.id)forlinself.sale_order_id.order_line])
            #removeSOLfortaskwithoutproduct
            #andifataskhasaproductthatmatchaproductfromaSOL,weputthisSOLontask.
            fortaskintask_no_sale_line:
                ifnottask.timesheet_product_id:
                    task.sale_line_id=False
                eliftask.timesheet_product_id.idindict_product_sol:
                    task.write({'sale_line_id':dict_product_sol[task.timesheet_product_id.id]})

    defaction_create_sale_order(self):
        #ifprojectlinkedtoSOlineoratleastontaskswithSOline,thenweconsiderprojectasbillable.
        ifself.project_id.sale_line_id:
            raiseUserError(_("Theprojectisalreadylinkedtoasalesorderitem."))
        #atleastoneline
        ifnotself.line_ids:
            raiseUserError(_("Atleastonelineshouldbefilled."))

        ifself.pricing_type=='employee_rate':
            #allemployeehavingtimesheetshouldbeinthewizardmap
            timesheet_employees=self.env['account.analytic.line'].search([('task_id','in',self.project_id.tasks.ids)]).mapped('employee_id')
            map_employees=self.line_ids.mapped('employee_id')
            missing_meployees=timesheet_employees-map_employees
            ifmissing_meployees:
                raiseUserError(_('TheSalesOrdercannotbecreatedbecauseyoudidnotentersomeemployeesthatenteredtimesheetsonthisproject.PleaselistalltherelevantemployeesbeforecreatingtheSalesOrder.\nMissingemployee(s):%s')%(','.join(missing_meployees.mapped('name'))))

        #checkhereiftimesheetalreadylinkedtoSOline
        timesheet_with_so_line=self.env['account.analytic.line'].search_count([('task_id','in',self.project_id.tasks.ids),('so_line','!=',False)])
        iftimesheet_with_so_line:
            raiseUserError(_('Thesalesordercannotbecreatedbecausesometimesheetsofthisprojectarealreadylinkedtoanothersalesorder.'))

        #createSOaccordingtothechosenbillabletype
        sale_order=self._create_sale_order()

        view_form_id=self.env.ref('sale.view_order_form').id
        action=self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action.update({
            'views':[(view_form_id,'form')],
            'view_mode':'form',
            'name':sale_order.name,
            'res_id':sale_order.id,
        })
        returnaction

    def_create_sale_order(self):
        """Privateimplementationofgeneratingthesalesorder"""
        sale_order=self.env['sale.order'].create({
            'project_id':self.project_id.id,
            'partner_id':self.partner_id.id,
            'analytic_account_id':self.project_id.analytic_account_id.id,
            'client_order_ref':self.project_id.name,
            'company_id':self.project_id.company_id.id,
        })
        sale_order.onchange_partner_id()
        sale_order.onchange_partner_shipping_id()
        #rewritetheuserastheonchange_partner_iderasesit
        sale_order.write({'user_id':self.project_id.user_id.id})
        sale_order.onchange_user_id()

        #createthesalelines,themap(optional),andassignexistingtimesheettosalelines
        self._make_billable(sale_order)

        #confirmSO
        sale_order.action_confirm()
        returnsale_order

    def_make_billable(self,sale_order):
        ifself.pricing_type=='fixed_rate':
            self._make_billable_at_project_rate(sale_order)
        else:
            self._make_billable_at_employee_rate(sale_order)

    def_make_billable_at_project_rate(self,sale_order):
        self.ensure_one()
        task_left=self.project_id.tasks.filtered(lambdatask:nottask.sale_line_id)
        ticket_timesheet_ids=self.env.context.get('ticket_timesheet_ids',[])
        forwizard_lineinself.line_ids:
            task_ids=self.project_id.tasks.filtered(lambdatask:nottask.sale_line_idandtask.timesheet_product_id==wizard_line.product_id)
            task_left-=task_ids
            #tryingtosimulatetheSOlinecreatedatask,accordingtotheproductconfiguration
            #Toavoid,generatingataskwhenconfirmingtheSO
            task_id=False
            iftask_idsandwizard_line.product_id.service_trackingin['task_in_project','task_global_project']:
                task_id=task_ids.ids[0]

            #createSOline
            sale_order_line=self.env['sale.order.line'].create({
                'order_id':sale_order.id,
                'product_id':wizard_line.product_id.id,
                'price_unit':wizard_line.price_unit,
                'project_id':self.project_id.id, #preventtore-createaprojectonconfirmation
                'task_id':task_id,
                'product_uom_qty':0.0,
            })

            ifticket_timesheet_idsandnotself.project_id.sale_line_idandnottask_ids:
                #Withpricing="projectrate"inproject.Whentheuserwantstocreateasaleorderfromaticketinhelpdesk
                #Theprojectcannotcontainanytasks.Thus,weneedtogivethefirstsale_order_linecreatedtolink
                #thetimesheettothisfirstsaleorderline.
                #linktheprojecttotheSOline
                self.project_id.write({
                    'sale_order_id':sale_order.id,
                    'sale_line_id':sale_order_line.id,
                    'partner_id':self.partner_id.id,
                })

            #linkthetaskstotheSOline
            task_ids.write({
                'sale_line_id':sale_order_line.id,
                'partner_id':sale_order.partner_id.id,
                'email_from':sale_order.partner_id.email,
            })

            #assignSOLtotimesheets
            search_domain=[('task_id','in',task_ids.ids),('so_line','=',False)]
            ifticket_timesheet_ids:
                search_domain=[('id','in',ticket_timesheet_ids),('so_line','=',False)]

            self.env['account.analytic.line'].search(search_domain).write({
                'so_line':sale_order_line.id
            })
            sale_order_line.with_context({'no_update_planned_hours':True}).write({
                'product_uom_qty':sale_order_line.qty_delivered
            })

        ifticket_timesheet_idsandself.project_id.sale_line_idandnotself.project_id.tasksandlen(self.line_ids)>1:
            #Then,weneedtogivetotheprojectthelastsaleorderlinecreated
            self.project_id.write({
                'sale_line_id':sale_order_line.id
            })
        else: #Otherwise,weareinthenormalbehaviour
            #linktheprojecttotheSOline
            self.project_id.write({
                'sale_order_id':sale_order.id,
                'sale_line_id':sale_order_line.id, #wetakethelastsale_order_linecreated
                'partner_id':self.partner_id.id,
            })

        iftask_left:
            task_left.sale_line_id=False

    def_make_billable_at_employee_rate(self,sale_order):
        #tryingtosimulatetheSOlinecreatedatask,accordingtotheproductconfiguration
        #Toavoid,generatingataskwhenconfirmingtheSO
        task_id=self.env['project.task'].search([('project_id','=',self.project_id.id)],order='create_dateDESC',limit=1).id
        project_id=self.project_id.id

        lines_already_present=dict([(l.employee_id.id,l)forlinself.project_id.sale_line_employee_ids])

        non_billable_tasks=self.project_id.tasks.filtered(lambdatask:nottask.sale_line_id)
        non_allow_billable_tasks=self.project_id.tasks.filtered(lambdatask:task.non_allow_billable)

        map_entries=self.env['project.sale.line.employee.map']
        EmployeeMap=self.env['project.sale.line.employee.map'].sudo()

        #createSOlines:createonSOLperproduct/price.SomanyemployeecanbelinkedtothesameSOL
        map_product_price_sol={} #(product_id,price)-->SOL
        forwizard_lineinself.line_ids:
            map_key=(wizard_line.product_id.id,wizard_line.price_unit)
            ifmap_keynotinmap_product_price_sol:
                values={
                    'order_id':sale_order.id,
                    'product_id':wizard_line.product_id.id,
                    'price_unit':wizard_line.price_unit,
                    'product_uom_qty':0.0,
                }
                ifwizard_line.product_id.service_trackingin['task_in_project','task_global_project']:
                    values['task_id']=task_id
                ifwizard_line.product_id.service_trackingin['task_in_project','project_only']:
                    values['project_id']=project_id

                sale_order_line=self.env['sale.order.line'].create(values)
                map_product_price_sol[map_key]=sale_order_line

            ifwizard_line.employee_id.idnotinlines_already_present:
                map_entries|=EmployeeMap.create({
                    'project_id':self.project_id.id,
                    'sale_line_id':map_product_price_sol[map_key].id,
                    'employee_id':wizard_line.employee_id.id,
                })
            else:
                map_entries|=lines_already_present[wizard_line.employee_id.id]
                lines_already_present[wizard_line.employee_id.id].write({
                    'sale_line_id':map_product_price_sol[map_key].id
                })

        #linktheprojecttotheSO
        self.project_id.write({
            'sale_order_id':sale_order.id,
            'sale_line_id':sale_order.order_line[0].id,
            'partner_id':self.partner_id.id,
        })
        non_billable_tasks.write({
            'partner_id':sale_order.partner_id.id,
            'email_from':sale_order.partner_id.email,
        })
        non_allow_billable_tasks.sale_line_id=False

        tasks=self.project_id.tasks.filtered(lambdat:nott.non_allow_billable)
        #assignSOLtotimesheets
        formap_entryinmap_entries:
            search_domain=[('employee_id','=',map_entry.employee_id.id),('so_line','=',False)]
            ticket_timesheet_ids=self.env.context.get('ticket_timesheet_ids',[])
            ifticket_timesheet_ids:
                search_domain.append(('id','in',ticket_timesheet_ids))
            else:
                search_domain.append(('task_id','in',tasks.ids))
            self.env['account.analytic.line'].search(search_domain).write({
                'so_line':map_entry.sale_line_id.id
            })
            map_entry.sale_line_id.with_context({'no_update_planned_hours':True}).write({
                'product_uom_qty':map_entry.sale_line_id.qty_delivered
            })

        returnmap_entries


classProjectCreateSalesOrderLine(models.TransientModel):
    _name='project.create.sale.order.line'
    _description='CreateSOLinefromproject'
    _order='id,create_date'

    wizard_id=fields.Many2one('project.create.sale.order',required=True)
    product_id=fields.Many2one('product.product',domain=[('type','=','service'),('invoice_policy','=','delivery'),('service_type','=','timesheet')],string="Service",
        help="Productofthesalesorderitem.Mustbeaserviceinvoicedbasedontimesheetsontasks.")
    price_unit=fields.Float("UnitPrice",help="Unitpriceofthesalesorderitem.")
    currency_id=fields.Many2one('res.currency',string="Currency")
    employee_id=fields.Many2one('hr.employee',string="Employee",help="Employeethathastimesheetsontheproject.")
    sale_line_id=fields.Many2one('sale.order.line',"SaleOrderItem",compute='_compute_sale_line_id',store=True,readonly=False)

    _sql_constraints=[
        ('unique_employee_per_wizard','UNIQUE(wizard_id,employee_id)',"Anemployeecannotbeselectedmorethanonceinthemapping.Pleaseremoveduplicate(s)andtryagain."),
    ]

    @api.onchange('product_id','sale_line_id')
    def_onchange_product_id(self):
        ifself.wizard_id.link_selection=='link':
            self.price_unit=self.sale_line_id.price_unit
            self.currency_id=self.sale_line_id.currency_id
        else:
            self.price_unit=self.product_id.lst_priceor0
            self.currency_id=self.product_id.currency_id

    @api.depends('wizard_id.sale_order_id')
    def_compute_sale_line_id(self):
        forlineinself:
            ifline.sale_line_idandline.sale_line_id.order_id!=line.wizard_id.sale_order_id:
                line.sale_line_id=False
