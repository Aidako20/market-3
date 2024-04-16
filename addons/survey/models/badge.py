#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classGamificationBadge(models.Model):
    _inherit='gamification.badge'

    survey_ids=fields.One2many('survey.survey','certification_badge_id','SurveyIds')
    survey_id=fields.Many2one('survey.survey','Survey',compute='_compute_survey_id',store=True)

    @api.depends('survey_ids.certification_badge_id')
    def_compute_survey_id(self):
        forbadgeinself:
            badge.survey_id=badge.survey_ids[0]ifbadge.survey_idselseNone
