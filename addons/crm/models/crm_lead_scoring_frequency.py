#-*-coding:utf-8-*-
fromflectraimportfields,models


classLeadScoringFrequency(models.Model):
    _name='crm.lead.scoring.frequency'
    _description='LeadScoringFrequency'

    variable=fields.Char('Variable',index=True)
    value=fields.Char('Value')
    won_count=fields.Float('WonCount',digits=(16,1)) #Floatbecauseweadd0.1toavoidzeroFrequencyissue
    lost_count=fields.Float('LostCount',digits=(16,1)) #Floatbecauseweadd0.1toavoidzeroFrequencyissue
    team_id=fields.Many2one('crm.team','SalesTeam')


classFrequencyField(models.Model):
    _name='crm.lead.scoring.frequency.field'
    _description='Fieldsthatcanbeusedforpredictiveleadscoringcomputation'

    name=fields.Char(related="field_id.field_description")
    field_id=fields.Many2one(
        'ir.model.fields',domain=[('model_id.model','=','crm.lead')],required=True,
        ondelete='cascade',
    )
