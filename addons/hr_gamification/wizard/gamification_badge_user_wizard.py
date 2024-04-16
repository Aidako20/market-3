#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError,AccessError


classGamificationBadgeUserWizard(models.TransientModel):
    _inherit='gamification.badge.user.wizard'

    employee_id=fields.Many2one('hr.employee',string='Employee',required=True)
    user_id=fields.Many2one('res.users',string='User',related='employee_id.user_id',
        store=False,readonly=True,compute_sudo=True)

    defaction_grant_badge(self):
        """Wizardactionforsendingabadgetoachosenemployee"""
        ifnotself.user_id:
            raiseUserError(_('Youcansendbadgesonlytoemployeeslinkedtoauser.'))

        ifself.env.uid==self.user_id.id:
            raiseUserError(_('Youcannotsendabadgetoyourself.'))

        values={
            'user_id':self.user_id.id,
            'sender_id':self.env.uid,
            'badge_id':self.badge_id.id,
            'employee_id':self.employee_id.id,
            'comment':self.comment,
        }

        returnself.env['gamification.badge.user'].create(values)._send_badge()
