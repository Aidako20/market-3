#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,_


classCourse(models.Model):
    _inherit="slide.channel"

    defaction_mass_mailing_attendees(self):
        domain=repr([('slide_channel_ids','in',self.ids)])
        mass_mailing_action=dict(
            name=_('MassMailCourseMembers'),
            type='ir.actions.act_window',
            res_model='mailing.mailing',
            view_mode='form',
            target='current',
            context=dict(
                default_mailing_model_id=self.env.ref('base.model_res_partner').id,
                default_mailing_domain=domain,
            ),
        )
        returnmass_mailing_action
