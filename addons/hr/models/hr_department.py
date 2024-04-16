#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError


classDepartment(models.Model):
    _name="hr.department"
    _description="Department"
    _inherit=['mail.thread']
    _order="name"
    _rec_name='complete_name'

    name=fields.Char('DepartmentName',required=True)
    complete_name=fields.Char('CompleteName',compute='_compute_complete_name',store=True)
    active=fields.Boolean('Active',default=True)
    company_id=fields.Many2one('res.company',string='Company',index=True,default=lambdaself:self.env.company)
    parent_id=fields.Many2one('hr.department',string='ParentDepartment',index=True,domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    child_ids=fields.One2many('hr.department','parent_id',string='ChildDepartments')
    manager_id=fields.Many2one('hr.employee',string='Manager',tracking=True,domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    member_ids=fields.One2many('hr.employee','department_id',string='Members',readonly=True)
    jobs_ids=fields.One2many('hr.job','department_id',string='Jobs')
    note=fields.Text('Note')
    color=fields.Integer('ColorIndex')

    defname_get(self):
        ifnotself.env.context.get('hierarchical_naming',True):
            return[(record.id,record.name)forrecordinself]
        returnsuper(Department,self).name_get()

    @api.model
    defname_create(self,name):
        returnself.create({'name':name}).name_get()[0]

    @api.depends('name','parent_id.complete_name')
    def_compute_complete_name(self):
        fordepartmentinself:
            ifdepartment.parent_id:
                department.complete_name='%s/%s'%(department.parent_id.complete_name,department.name)
            else:
                department.complete_name=department.name

    @api.constrains('parent_id')
    def_check_parent_id(self):
        ifnotself._check_recursion():
            raiseValidationError(_('Youcannotcreaterecursivedepartments.'))

    @api.model
    defcreate(self,vals):
        #TDEnote:auto-subscriptionofmanagerdonebyhand,becausecurrently
        #thetrackingallowstotrack+subscribefieldslinkedtoares.userrecord
        #Anupdateofthelimitedbehaviorshouldcome,butnotcurrentlydone.
        department=super(Department,self.with_context(mail_create_nosubscribe=True)).create(vals)
        manager=self.env['hr.employee'].browse(vals.get("manager_id"))
        ifmanager.user_id:
            department.message_subscribe(partner_ids=manager.user_id.partner_id.ids)
        returndepartment

    defwrite(self,vals):
        """Ifupdatingmanagerofadepartment,weneedtoupdatealltheemployees
            ofdepartmenthierarchy,andsubscribethenewmanager.
        """
        #TDEnote:auto-subscriptionofmanagerdonebyhand,becausecurrently
        #thetrackingallowstotrack+subscribefieldslinkedtoares.userrecord
        #Anupdateofthelimitedbehaviorshouldcome,butnotcurrentlydone.
        if'manager_id'invals:
            manager_id=vals.get("manager_id")
            ifmanager_id:
                manager=self.env['hr.employee'].browse(manager_id)
                #subscribethemanageruser
                ifmanager.user_id:
                    self.message_subscribe(partner_ids=manager.user_id.partner_id.ids)
            #settheemployees'sparenttothenewmanager
            self._update_employee_manager(manager_id)
        returnsuper(Department,self).write(vals)

    def_update_employee_manager(self,manager_id):
        employees=self.env['hr.employee']
        fordepartmentinself:
            employees=employees|self.env['hr.employee'].search([
                ('id','!=',manager_id),
                ('department_id','=',department.id),
                ('parent_id','=',department.manager_id.id)
            ])
        employees.write({'parent_id':manager_id})
