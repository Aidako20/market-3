#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_,exceptions


classgrant_badge_wizard(models.TransientModel):
    """Wizardallowingtograntabadgetoauser"""
    _name='gamification.badge.user.wizard'
    _description='GamificationUserBadgeWizard'

    user_id=fields.Many2one("res.users",string='User',required=True)
    badge_id=fields.Many2one("gamification.badge",string='Badge',required=True)
    comment=fields.Text('Comment')

    defaction_grant_badge(self):
        """Wizardactionforsendingabadgetoachosenuser"""

        BadgeUser=self.env['gamification.badge.user']

        uid=self.env.uid
        forwizinself:
            ifuid==wiz.user_id.id:
                raiseexceptions.UserError(_('Youcannotgrantabadgetoyourself.'))

            #createthebadge
            BadgeUser.create({
                'user_id':wiz.user_id.id,
                'sender_id':uid,
                'badge_id':wiz.badge_id.id,
                'comment':wiz.comment,
            })._send_badge()

        returnTrue
