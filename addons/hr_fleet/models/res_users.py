#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields


classUser(models.Model):
    _inherit=['res.users']

    employee_cars_count=fields.Integer(related='employee_id.employee_cars_count')

    def__init__(self,pool,cr):
        """Overrideof__init__toaddaccessrights.
            Accessrightsaredisabledbydefault,butallowed
            onsomespecificfieldsdefinedinself.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        init_res=super(User,self).__init__(pool,cr)
        #duplicatelisttoavoidmodifyingtheoriginalreference
        pool[self._name].SELF_READABLE_FIELDS=pool[self._name].SELF_READABLE_FIELDS+['employee_cars_count']
        returninit_res

    defaction_get_claim_report(self):
        returnself.employee_id.action_get_claim_report()

    defaction_open_employee_cars(self):
        returnself.employee_id.action_open_employee_cars()
