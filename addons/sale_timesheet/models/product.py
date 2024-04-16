#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importthreading

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError


classProductTemplate(models.Model):
    _inherit='product.template'

    service_policy=fields.Selection([
        ('ordered_timesheet','Prepaid'),
        ('delivered_timesheet','Timesheetsontasks'),
        ('delivered_manual','Milestones(manuallysetquantitiesonorder)')
    ],string="ServiceInvoicingPolicy",compute='_compute_service_policy',inverse='_inverse_service_policy')
    service_type=fields.Selection(selection_add=[
        ('timesheet','Timesheetsonproject(onefareperSO/Project)'),
    ],ondelete={'timesheet':'setdefault'})
    #overridedomain
    project_id=fields.Many2one(domain="[('company_id','=',current_company_id),('allow_billable','=',True),('bill_type','=','customer_task'),('allow_timesheets','in',[service_policy=='delivered_timesheet',True])]")
    project_template_id=fields.Many2one(domain="[('company_id','=',current_company_id),('allow_billable','=',True),('bill_type','=','customer_project'),('allow_timesheets','in',[service_policy=='delivered_timesheet',True])]")

    def_default_visible_expense_policy(self):
        visibility=self.user_has_groups('project.group_project_user')
        returnvisibilityorsuper(ProductTemplate,self)._default_visible_expense_policy()

    def_compute_visible_expense_policy(self):
        visibility=self.user_has_groups('project.group_project_user')
        forproduct_templateinself:
            ifnotproduct_template.visible_expense_policy:
                product_template.visible_expense_policy=visibility
        returnsuper(ProductTemplate,self)._compute_visible_expense_policy()

    @api.depends('invoice_policy','service_type')
    def_compute_service_policy(self):
        forproductinself:
            policy=None
            ifproduct.invoice_policy=='delivery':
                policy='delivered_manual'ifproduct.service_type=='manual'else'delivered_timesheet'
            elifproduct.invoice_policy=='order'and(product.service_type=='timesheet'orproduct.type=='service'):
                policy='ordered_timesheet'
            product.service_policy=policy

    def_inverse_service_policy(self):
        forproductinself:
            policy=product.service_policy
            ifnotpolicyandnotproduct.invoice_policy=='delivery':
                product.invoice_policy='order'
                product.service_type='manual'
            elifpolicy=='ordered_timesheet':
                product.invoice_policy='order'
                product.service_type='timesheet'
            else:
                product.invoice_policy='delivery'
                product.service_type='manual'ifpolicy=='delivered_manual'else'timesheet'

    @api.onchange('type')
    def_onchange_type(self):
        res=super(ProductTemplate,self)._onchange_type()
        ifself.type=='service'andnotself.invoice_policy:
            self.invoice_policy='order'
            self.service_type='timesheet'
        elifself.type=='service'andself.invoice_policy=='order':
            self.service_policy='ordered_timesheet'
        elifself.type=='consu'andnotself.invoice_policyandself.service_policy=='ordered_timesheet':
            self.invoice_policy='order'

        ifself.type!='service':
            self.service_tracking='no'
        returnres

    @api.model
    def_get_onchange_service_policy_updates(self,service_tracking,service_policy,project_id,project_template_id):
        vals={}
        ifservice_tracking!='no'andservice_policy=='delivered_timesheet':
            ifproject_idandnotproject_id.allow_timesheets:
                vals['project_id']=False
            elifproject_template_idandnotproject_template_id.allow_timesheets:
                vals['project_template_id']=False
        returnvals

    @api.onchange('service_policy')
    def_onchange_service_policy(self):
        vals=self._get_onchange_service_policy_updates(self.service_tracking,
                                                        self.service_policy,
                                                        self.project_id,
                                                        self.project_template_id)
        ifvals:
            self.update(vals)

    defunlink(self):
        time_product=self.env.ref('sale_timesheet.time_product')
        iftime_product.product_tmpl_idinself:
            raiseValidationError(_('The%sproductisrequiredbytheTimesheetappandcannotbearchived/deleted.')%time_product.name)
        returnsuper(ProductTemplate,self).unlink()

    defwrite(self,vals):
        #timesheetproductcan'tbearchived
        test_mode=getattr(threading.currentThread(),'testing',False)orself.env.registry.in_test_mode()
        ifnottest_modeand'active'invalsandnotvals['active']:
            time_product=self.env.ref('sale_timesheet.time_product')
            iftime_product.product_tmpl_idinself:
                raiseValidationError(_('The%sproductisrequiredbytheTimesheetappandcannotbearchived/deleted.')%time_product.name)
        if'type'invalsandvals['type']!='service':
            vals.update({
                'service_tracking':'no',
                'project_id':False
            })
        returnsuper(ProductTemplate,self).write(vals)


classProductProduct(models.Model):
    _inherit='product.product'

    def_is_delivered_timesheet(self):
        """Checkiftheproductisadeliveredtimesheet"""
        self.ensure_one()
        returnself.type=='service'andself.service_policy=='delivered_timesheet'

    @api.onchange('service_policy')
    def_onchange_service_policy(self):
        vals=self.product_tmpl_id._get_onchange_service_policy_updates(self.service_tracking,
                                                                        self.service_policy,
                                                                        self.project_id,
                                                                        self.project_template_id)
        ifvals:
            self.update(vals)

    @api.onchange('type')
    def_onchange_type(self):
        res=super(ProductProduct,self)._onchange_type()
        ifself.type!='service':
            self.service_tracking='no'
        returnres

    defunlink(self):
        time_product=self.env.ref('sale_timesheet.time_product')
        iftime_productinself:
            raiseValidationError(_('The%sproductisrequiredbytheTimesheetappandcannotbearchived/deleted.')%time_product.name)
        returnsuper(ProductProduct,self).unlink()

    defwrite(self,vals):
        #timesheetproductcan'tbearchived
        test_mode=getattr(threading.currentThread(),'testing',False)orself.env.registry.in_test_mode()
        ifnottest_modeand'active'invalsandnotvals['active']:
            time_product=self.env.ref('sale_timesheet.time_product')
            iftime_productinself:
                raiseValidationError(_('The%sproductisrequiredbytheTimesheetappandcannotbearchived/deleted.')%time_product.name)
        if'type'invalsandvals['type']!='service':
            vals.update({
                'service_tracking':'no',
                'project_id':False
            })
        returnsuper(ProductProduct,self).write(vals)
