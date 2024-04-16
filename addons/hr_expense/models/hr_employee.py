#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api


classEmployee(models.Model):
    _inherit='hr.employee'

    def_group_hr_expense_user_domain(self):
        #Wereturnthedomainonlyifthegroupexistsforthefollowingreason:
        #Whenagroupiscreated(atmoduleinstallation),the`res.users`formviewis
        #automaticallymodifiedtoaddapplicationaccesses.Whenmodifiyingtheview,it
        #readstherelatedfield`expense_manager_id`of`res.users`andretrieveitsdomain.
        #Thisisaproblembecausethe`group_hr_expense_user`recordhasalreadybeencreatedbut
        #notitsassociated`ir.model.data`whichmakes`self.env.ref(...)`fail.
        group=self.env.ref('hr_expense.group_hr_expense_team_approver',raise_if_not_found=False)
        return[('groups_id','in',group.ids)]ifgroupelse[]

    expense_manager_id=fields.Many2one(
        'res.users',string='Expense',
        domain=_group_hr_expense_user_domain,
        compute='_compute_expense_manager',store=True,readonly=False,
        help='Selecttheuserresponsibleforapproving"Expenses"ofthisemployee.\n'
             'Ifempty,theapprovalisdonebyanAdministratororApprover(determinedinsettings/users).')

    @api.depends('parent_id')
    def_compute_expense_manager(self):
        foremployeeinself:
            previous_manager=employee._origin.parent_id.user_id
            manager=employee.parent_id.user_id
            ifmanagerandmanager.has_group('hr_expense.group_hr_expense_user')and(employee.expense_manager_id==previous_managerornotemployee.expense_manager_id):
                employee.expense_manager_id=manager
            elifnotemployee.expense_manager_id:
                employee.expense_manager_id=False


classEmployeePublic(models.Model):
    _inherit='hr.employee.public'

    expense_manager_id=fields.Many2one('res.users',readonly=True)


classUser(models.Model):
    _inherit=['res.users']

    expense_manager_id=fields.Many2one(related='employee_id.expense_manager_id',readonly=False)

    def__init__(self,pool,cr):
        """Overrideof__init__toaddaccessrights.
            Accessrightsaredisabledbydefault,butallowed
            onsomespecificfieldsdefinedinself.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        init_res=super(User,self).__init__(pool,cr)
        #duplicatelisttoavoidmodifyingtheoriginalreference
        pool[self._name].SELF_READABLE_FIELDS=pool[self._name].SELF_READABLE_FIELDS+['expense_manager_id']
        returninit_res
