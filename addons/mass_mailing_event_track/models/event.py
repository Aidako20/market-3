#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classEvent(models.Model):
    _inherit="event.event"

    defaction_mass_mailing_track_speakers(self):
        mass_mailing_action=dict(
            name='MassMailAttendees',
            type='ir.actions.act_window',
            res_model='mailing.mailing',
            view_mode='form',
            target='current',
            context=dict(
                default_mailing_model_id=self.env.ref('website_event_track.model_event_track').id,
                default_mailing_domain=repr([('event_id','in',self.ids),('stage_id.is_cancel','!=',True)]),
            ),
        )
        returnmass_mailing_action
