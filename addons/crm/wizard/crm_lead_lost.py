#-*-coding:utf-8-*-

fromflectraimportapi,fields,models


classCrmLeadLost(models.TransientModel):
    _name='crm.lead.lost'
    _description='GetLostReason'

    lost_reason_id=fields.Many2one('crm.lost.reason','LostReason')

    defaction_lost_reason_apply(self):
        leads=self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        returnleads.action_set_lost(lost_reason=self.lost_reason_id.id)
