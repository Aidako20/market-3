#-*-coding:utf-8-*-

fromflectraimportapi,fields,models,tools


classMaintenanceEquipment(models.Model):
    _inherit='maintenance.equipment'

    employee_id=fields.Many2one('hr.employee',compute='_compute_equipment_assign',
        store=True,readonly=False,string='AssignedEmployee',tracking=True)
    department_id=fields.Many2one('hr.department',compute='_compute_equipment_assign',
        store=True,readonly=False,string='AssignedDepartment',tracking=True)
    equipment_assign_to=fields.Selection(
        [('department','Department'),('employee','Employee'),('other','Other')],
        string='UsedBy',
        required=True,
        default='employee')
    owner_user_id=fields.Many2one(compute='_compute_owner',store=True)
    assign_date=fields.Date(compute='_compute_equipment_assign',store=True,readonly=False,copy=True)

    @api.depends('employee_id','department_id','equipment_assign_to')
    def_compute_owner(self):
        forequipmentinself:
            equipment.owner_user_id=self.env.user.id
            ifequipment.equipment_assign_to=='employee':
                equipment.owner_user_id=equipment.employee_id.user_id.id
            elifequipment.equipment_assign_to=='department':
                equipment.owner_user_id=equipment.department_id.manager_id.user_id.id

    @api.depends('equipment_assign_to')
    def_compute_equipment_assign(self):
        forequipmentinself:
            ifequipment.equipment_assign_to=='employee':
                equipment.department_id=False
                equipment.employee_id=equipment.employee_id
            elifequipment.equipment_assign_to=='department':
                equipment.employee_id=False
                equipment.department_id=equipment.department_id
            else:
                equipment.department_id=equipment.department_id
                equipment.employee_id=equipment.employee_id
            equipment.assign_date=fields.Date.context_today(self)

    @api.model
    defcreate(self,vals):
        equipment=super(MaintenanceEquipment,self).create(vals)
        #subscribeemployeeordepartmentmanagerwhenequipmentassigntohim.
        partner_ids=[]
        ifequipment.employee_idandequipment.employee_id.user_id:
            partner_ids.append(equipment.employee_id.user_id.partner_id.id)
        ifequipment.department_idandequipment.department_id.manager_idandequipment.department_id.manager_id.user_id:
            partner_ids.append(equipment.department_id.manager_id.user_id.partner_id.id)
        ifpartner_ids:
            equipment.message_subscribe(partner_ids=partner_ids)
        returnequipment

    defwrite(self,vals):
        partner_ids=[]
        #subscribeemployeeordepartmentmanagerwhenequipmentassigntoemployeeordepartment.
        ifvals.get('employee_id'):
            user_id=self.env['hr.employee'].browse(vals['employee_id'])['user_id']
            ifuser_id:
                partner_ids.append(user_id.partner_id.id)
        ifvals.get('department_id'):
            department=self.env['hr.department'].browse(vals['department_id'])
            ifdepartmentanddepartment.manager_idanddepartment.manager_id.user_id:
                partner_ids.append(department.manager_id.user_id.partner_id.id)
        ifpartner_ids:
            self.message_subscribe(partner_ids=partner_ids)
        returnsuper(MaintenanceEquipment,self).write(vals)

    def_track_subtype(self,init_values):
        self.ensure_one()
        if('employee_id'ininit_valuesandself.employee_id)or('department_id'ininit_valuesandself.department_id):
            returnself.env.ref('maintenance.mt_mat_assign')
        returnsuper(MaintenanceEquipment,self)._track_subtype(init_values)


classMaintenanceRequest(models.Model):
    _inherit='maintenance.request'

    @api.returns('self')
    def_default_employee_get(self):
        returnself.env.user.employee_id

    employee_id=fields.Many2one('hr.employee',string='Employee',default=_default_employee_get)
    owner_user_id=fields.Many2one(compute='_compute_owner',store=True)
    equipment_id=fields.Many2one(domain="['|',('employee_id','=',employee_id),('employee_id','=',False)]")

    @api.depends('employee_id')
    def_compute_owner(self):
        forrinself:
            ifr.equipment_id.equipment_assign_to=='employee':
                r.owner_user_id=r.employee_id.user_id.id
            else:
                r.owner_user_id=False

    @api.model
    defcreate(self,vals):
        result=super(MaintenanceRequest,self).create(vals)
        ifresult.employee_id.user_id:
            result.message_subscribe(partner_ids=[result.employee_id.user_id.partner_id.id])
        returnresult

    defwrite(self,vals):
        ifvals.get('employee_id'):
            employee=self.env['hr.employee'].browse(vals['employee_id'])
            ifemployeeandemployee.user_id:
                self.message_subscribe(partner_ids=[employee.user_id.partner_id.id])
        returnsuper(MaintenanceRequest,self).write(vals)

    @api.model
    defmessage_new(self,msg,custom_values=None):
        """Overridesmail_threadmessage_newthatiscalledbythemailgateway
            throughmessage_process.
            Thisoverrideupdatesthedocumentaccordingtotheemail.
        """
        ifcustom_valuesisNone:
            custom_values={}
        email=tools.email_split(msg.get('from'))andtools.email_split(msg.get('from'))[0]orFalse
        user=self.env['res.users'].search([('login','=',email)],limit=1)
        ifuser:
            employee=self.env.user.employee_id
            ifemployee:
                custom_values['employee_id']=employeeandemployee[0].id
        returnsuper(MaintenanceRequest,self).message_new(msg,custom_values=custom_values)
