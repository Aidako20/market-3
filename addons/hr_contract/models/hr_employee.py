#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models
fromflectra.osvimportexpression


classEmployee(models.Model):
    _inherit="hr.employee"

    vehicle=fields.Char(string='CompanyVehicle',groups="hr.group_hr_user")
    contract_ids=fields.One2many('hr.contract','employee_id',string='EmployeeContracts')
    contract_id=fields.Many2one('hr.contract',string='CurrentContract',
        groups="hr.group_hr_user",domain="[('company_id','=',company_id)]",help='Currentcontractoftheemployee')
    calendar_mismatch=fields.Boolean(related='contract_id.calendar_mismatch')
    contracts_count=fields.Integer(compute='_compute_contracts_count',string='ContractCount')
    contract_warning=fields.Boolean(string='ContractWarning',store=True,compute='_compute_contract_warning',groups="hr.group_hr_user")
    first_contract_date=fields.Date(compute='_compute_first_contract_date',groups="hr.group_hr_user")

    def_get_first_contracts(self):
        self.ensure_one()
        returnself.sudo().contract_ids.filtered(lambdac:c.state!='cancel')

    @api.depends('contract_ids.state','contract_ids.date_start')
    def_compute_first_contract_date(self):
        foremployeeinself:
            contracts=employee._get_first_contracts()
            ifcontracts:
                employee.first_contract_date=min(contracts.mapped('date_start'))
            else:
                employee.first_contract_date=False

    @api.depends('contract_id','contract_id.state','contract_id.kanban_state')
    def_compute_contract_warning(self):
        foremployeeinself:
            employee.contract_warning=notemployee.contract_idoremployee.contract_id.kanban_state=='blocked'oremployee.contract_id.state!='open'

    def_compute_contracts_count(self):
        #read_groupassudo,sincecontractcountisdisplayedonformview
        contract_data=self.env['hr.contract'].sudo().read_group([('employee_id','in',self.ids)],['employee_id'],['employee_id'])
        result=dict((data['employee_id'][0],data['employee_id_count'])fordataincontract_data)
        foremployeeinself:
            employee.contracts_count=result.get(employee.id,0)

    def_get_contracts(self,date_from,date_to,states=['open'],kanban_state=False):
        """
        Returnsthecontractsoftheemployeebetweendate_fromanddate_to
        """
        state_domain=[('state','in',states)]
        ifkanban_state:
            state_domain=expression.AND([state_domain,[('kanban_state','in',kanban_state)]])

        returnself.env['hr.contract'].search(
            expression.AND([[('employee_id','in',self.ids)],
            state_domain,
            [('date_start','<=',date_to),
                '|',
                    ('date_end','=',False),
                    ('date_end','>=',date_from)]]))

    def_get_incoming_contracts(self,date_from,date_to):
        returnself._get_contracts(date_from,date_to,states=['draft'],kanban_state=['done'])

    @api.model
    def_get_all_contracts(self,date_from,date_to,states=['open']):
        """
        Returnsthecontractsofallemployeesbetweendate_fromanddate_to
        """
        returnself.search([])._get_contracts(date_from,date_to,states=states)

    defwrite(self,vals):
        res=super(Employee,self).write(vals)
        ifvals.get('contract_id'):
            foremployeeinself:
                employee.resource_calendar_id.transfer_leaves_to(employee.contract_id.resource_calendar_id,employee.resource_id)
                employee.resource_calendar_id=employee.contract_id.resource_calendar_id
        returnres
