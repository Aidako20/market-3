#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,fields

classgoal_manual_wizard(models.TransientModel):
    """Wizardtoupdateamanualgoal"""
    _name='gamification.goal.wizard'
    _description='GamificationGoalWizard'

    goal_id=fields.Many2one("gamification.goal",string='Goal',required=True)
    current=fields.Float('Current')

    defaction_update_current(self):
        """Wizardactionforupdatingthecurrentvalue"""
        forwizinself:
            wiz.goal_id.write({
                'current':wiz.current,
                'goal_id':wiz.goal_id.id,
                'to_update':False,
            })
            wiz.goal_id.update_goal()

        returnFalse
