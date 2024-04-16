#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classUser(models.Model):
    _inherit="res.users"

    leave_manager_id=fields.Many2one(related='employee_id.leave_manager_id')
    show_leaves=fields.Boolean(related='employee_id.show_leaves')
    allocation_used_count=fields.Float(related='employee_id.allocation_used_count')
    allocation_count=fields.Float(related='employee_id.allocation_count')
    leave_date_to=fields.Date(related='employee_id.leave_date_to')
    current_leave_state=fields.Selection(related='employee_id.current_leave_state')
    is_absent=fields.Boolean(related='employee_id.is_absent')
    allocation_used_display=fields.Char(related='employee_id.allocation_used_display')
    allocation_display=fields.Char(related='employee_id.allocation_display')
    hr_icon_display=fields.Selection(related='employee_id.hr_icon_display')

    def__init__(self,pool,cr):
        """Overrideof__init__toaddaccessrights.
            Accessrightsaredisabledbydefault,butallowed
            onsomespecificfieldsdefinedinself.SELF_{READ/WRITE}ABLE_FIELDS.
        """

        readable_fields=[
            'leave_manager_id',
            'show_leaves',
            'allocation_used_count',
            'allocation_count',
            'leave_date_to',
            'current_leave_state',
            'is_absent',
            'allocation_used_display',
            'allocation_display',
            'hr_icon_display',
        ]
        init_res=super(User,self).__init__(pool,cr)
        #duplicatelisttoavoidmodifyingtheoriginalreference
        pool[self._name].SELF_READABLE_FIELDS=pool[self._name].SELF_READABLE_FIELDS+readable_fields
        returninit_res

    def_compute_im_status(self):
        super(User,self)._compute_im_status()
        on_leave_user_ids=self._get_on_leave_ids()
        foruserinself:
            ifuser.idinon_leave_user_ids:
                ifuser.im_status=='online':
                    user.im_status='leave_online'
                else:
                    user.im_status='leave_offline'

    @api.model
    def_get_on_leave_ids(self,partner=False):
        now=fields.Datetime.now()
        field='partner_id'ifpartnerelse'id'
        self.env.cr.execute('''SELECTres_users.%sFROMres_users
                            JOINhr_leaveONhr_leave.user_id=res_users.id
                            ANDstatein('validate')
                            ANDres_users.active='t'
                            ANDdate_from<=%%sANDdate_to>=%%s'''%field,(now,now))
        return[r[0]forrinself.env.cr.fetchall()]

    def_clean_leave_responsible_users(self):
        #self=oldbunchofleaveresponsibles
        #Thismethodcomparesthecurrentleavemanagers
        #andremovetheaccessrightstothosewhodon't
        #needthemanymore
        approver_group=self.env.ref('hr_holidays.group_hr_holidays_responsible',raise_if_not_found=False)
        ifnotselfornotapprover_group:
            return
        res=self.env['hr.employee'].read_group(
            [('leave_manager_id','in',self.ids)],
            ['leave_manager_id'],
            ['leave_manager_id'])
        responsibles_to_remove_ids=set(self.ids)-{x['leave_manager_id'][0]forxinres}
        approver_group.sudo().write({
            'users':[(3,manager_id)formanager_idinresponsibles_to_remove_ids]})
