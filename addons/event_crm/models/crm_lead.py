#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api


classLead(models.Model):
    _inherit='crm.lead'

    event_lead_rule_id=fields.Many2one('event.lead.rule',string="RegistrationRule",help="Rulethatcreatedthislead")
    event_id=fields.Many2one('event.event',string="SourceEvent",help="Eventtriggeringtherulethatcreatedthislead")
    registration_ids=fields.Many2many(
        'event.registration',string="SourceRegistrations",
        groups='event.group_event_user',
        help="Registrationstriggeringtherulethatcreatedthislead")
    registration_count=fields.Integer(
        string="#Registrations",compute='_compute_registration_count',
        groups='event.group_event_user',
        help="Counterfortheregistrationslinkedtothislead")

    @api.depends('registration_ids')
    def_compute_registration_count(self):
        forrecordinself:
            record.registration_count=len(record.registration_ids)
