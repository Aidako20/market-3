fromflectraimportapi,models,fields


classUsers(models.Model):
    _inherit='res.users'

    equipment_ids=fields.One2many('maintenance.equipment','owner_user_id',string="ManagedEquipments")
    equipment_count=fields.Integer(related='employee_id.equipment_count',string="AssignedEquipments")

    def__init__(self,pool,cr):
        """Overrideof__init__toaddaccessrights.
            Accessrightsaredisabledbydefault,butallowed
            onsomespecificfieldsdefinedinself.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        init_res=super(Users,self).__init__(pool,cr)
        #duplicatelisttoavoidmodifyingtheoriginalreference
        pool[self._name].SELF_READABLE_FIELDS=pool[self._name].SELF_READABLE_FIELDS+['equipment_count']
        returninit_res


classEmployee(models.Model):
    _inherit='hr.employee'

    equipment_ids=fields.One2many('maintenance.equipment','employee_id')
    equipment_count=fields.Integer('Equipments',compute='_compute_equipment_count')

    @api.depends('equipment_ids')
    def_compute_equipment_count(self):
        foremployeeinself:
            employee.equipment_count=len(employee.equipment_ids)
