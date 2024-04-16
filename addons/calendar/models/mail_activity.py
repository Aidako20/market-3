#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,fields,tools,_


classMailActivityType(models.Model):
    _inherit="mail.activity.type"

    category=fields.Selection(selection_add=[('meeting','Meeting')])


classMailActivity(models.Model):
    _inherit="mail.activity"

    calendar_event_id=fields.Many2one('calendar.event',string="CalendarMeeting",ondelete='cascade')

    defaction_create_calendar_event(self):
        self.ensure_one()
        action=self.env["ir.actions.actions"]._for_xml_id("calendar.action_calendar_event")
        action['context']={
            'default_activity_type_id':self.activity_type_id.id,
            'default_res_id':self.env.context.get('default_res_id'),
            'default_res_model':self.env.context.get('default_res_model'),
            'default_name':self.summaryorself.res_name,
            'default_description':self.noteandtools.html2plaintext(self.note).strip()or'',
            'default_activity_ids':[(6,0,self.ids)],
        }
        returnaction

    def_action_done(self,feedback=False,attachment_ids=False):
        events=self.mapped('calendar_event_id')
        messages,activities=super(MailActivity,self)._action_done(feedback=feedback,attachment_ids=attachment_ids)
        iffeedback:
            foreventinevents:
                description=event.description
                description='%s\n%s%s'%(descriptionor'',_("Feedback:"),feedback)
                event.write({'description':description})
        returnmessages,activities

    defunlink_w_meeting(self):
        events=self.mapped('calendar_event_id')
        res=self.unlink()
        events.unlink()
        returnres
