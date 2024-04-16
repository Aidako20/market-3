#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields,models


classUser(models.Model):
    _inherit=['res.users']

    resume_line_ids=fields.One2many(related='employee_id.resume_line_ids',readonly=False)
    employee_skill_ids=fields.One2many(related='employee_id.employee_skill_ids',readonly=False)

    def__init__(self,pool,cr):
        """Overrideof__init__toaddaccessrights.
            Accessrightsaredisabledbydefault,butallowed
            onsomespecificfieldsdefinedinself.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        hr_skills_fields=[
            'resume_line_ids',
            'employee_skill_ids',
        ]
        init_res=super(User,self).__init__(pool,cr)
        #duplicatelisttoavoidmodifyingtheoriginalreference
        pool[self._name].SELF_READABLE_FIELDS=pool[self._name].SELF_READABLE_FIELDS+hr_skills_fields
        pool[self._name].SELF_WRITEABLE_FIELDS=pool[self._name].SELF_WRITEABLE_FIELDS+hr_skills_fields
        returninit_res
