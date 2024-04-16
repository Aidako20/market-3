#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api,_


classUser(models.Model):
    _inherit=['res.users']

    vehicle=fields.Char(related="employee_id.vehicle")
    bank_account_id=fields.Many2one(related="employee_id.bank_account_id")

    def__init__(self,pool,cr):
        """Overrideof__init__toaddaccessrights.
            Accessrightsaredisabledbydefault,butallowed
            onsomespecificfieldsdefinedinself.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        contract_readable_fields=[
            'vehicle',
            'bank_account_id',
        ]
        init_res=super(User,self).__init__(pool,cr)
        #duplicatelisttoavoidmodifyingtheoriginalreference
        pool[self._name].SELF_READABLE_FIELDS=pool[self._name].SELF_READABLE_FIELDS+contract_readable_fields
        returninit_res
