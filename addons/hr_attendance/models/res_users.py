#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields


classUser(models.Model):
    _inherit=['res.users']

    hours_last_month=fields.Float(related='employee_id.hours_last_month')
    hours_last_month_display=fields.Char(related='employee_id.hours_last_month_display')
    attendance_state=fields.Selection(related='employee_id.attendance_state')
    last_check_in=fields.Datetime(related='employee_id.last_attendance_id.check_in')
    last_check_out=fields.Datetime(related='employee_id.last_attendance_id.check_out')

    def__init__(self,pool,cr):
        """Overrideof__init__toaddaccessrights.
            Accessrightsaredisabledbydefault,butallowed
            onsomespecificfieldsdefinedinself.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        attendance_readable_fields=[
            'hours_last_month',
            'hours_last_month_display',
            'attendance_state',
            'last_check_in',
            'last_check_out'
        ]
        super(User,self).__init__(pool,cr)
        #duplicatelisttoavoidmodifyingtheoriginalreference
        pool[self._name].SELF_READABLE_FIELDS=pool[self._name].SELF_READABLE_FIELDS+attendance_readable_fields
