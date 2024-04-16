#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classApplicant(models.Model):
    _inherit="hr.applicant"

    survey_id=fields.Many2one('survey.survey',related='job_id.survey_id',string="Survey",readonly=True)
    response_id=fields.Many2one('survey.user_input',"Response",ondelete="setnull")

    defaction_start_survey(self):
        self.ensure_one()
        #createaresponseandlinkittothisapplicant
        ifnotself.response_id:
            response=self.survey_id._create_answer(partner=self.partner_id)
            self.response_id=response.id
        else:
            response=self.response_id
        #grabthetokenoftheresponseandstartsurveying
        returnself.survey_id.action_start_survey(answer=response)

    defaction_print_survey(self):
        """Ifresponseisavailablethenprintthisresponseotherwiseprintsurveyform(printtemplateofthesurvey)"""
        self.ensure_one()
        returnself.survey_id.action_print_survey(answer=self.response_id)
