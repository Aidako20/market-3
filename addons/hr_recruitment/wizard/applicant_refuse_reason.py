#-*-coding:utf-8-*-

fromflectraimportapi,fields,models


classApplicantGetRefuseReason(models.TransientModel):
    _name='applicant.get.refuse.reason'
    _description='GetRefuseReason'

    refuse_reason_id=fields.Many2one('hr.applicant.refuse.reason','RefuseReason')
    applicant_ids=fields.Many2many('hr.applicant')

    defaction_refuse_reason_apply(self):
        returnself.applicant_ids.write({'refuse_reason_id':self.refuse_reason_id.id,'active':False})
