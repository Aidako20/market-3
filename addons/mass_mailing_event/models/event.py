#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,_


classEvent(models.Model):
    _inherit="event.event"

    defaction_mass_mailing_attendees(self):
        return{
            'name':'MassMailAttendees',
            'type':'ir.actions.act_window',
            'res_model':'mailing.mailing',
            'view_mode':'form',
            'target':'current',
            'context':{
                'default_mailing_model_id':self.env.ref('event.model_event_registration').id,
                'default_mailing_domain':repr([('event_id','in',self.ids),('state','!=','cancel')])
            },
        }

    defaction_invite_contacts(self):
        return{
            'name':'MassMailInvitation',
            'type':'ir.actions.act_window',
            'res_model':'mailing.mailing',
            'view_mode':'form',
            'target':'current',
            'context':{'default_mailing_model_id':self.env.ref('base.model_res_partner').id},
        }
