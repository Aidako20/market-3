#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api


classEventEvent(models.Model):
    _name="event.event"
    _inherit="event.event"

    lead_ids=fields.One2many(
        'crm.lead','event_id',string="Leads",groups='sales_team.group_sale_salesman',
        help="Leadsgeneratedfromthisevent")
    lead_count=fields.Integer(
        string="#Leads",compute='_compute_lead_count',groups='sales_team.group_sale_salesman',
        help="Counterfortheleadslinkedtothisevent")

    @api.depends('lead_ids')
    def_compute_lead_count(self):
        lead_data=self.env['crm.lead'].read_group(
            [('event_id','in',self.ids)],
            ['event_id'],['event_id']
        )
        mapped_data={item['event_id'][0]:item['event_id_count']foriteminlead_data}
        foreventinself:
            event.lead_count=mapped_data.get(event.id,0)
