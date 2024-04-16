#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models
fromflectra.toolsimporthtml2plaintext


classSurveyUserInput(models.Model):
    _inherit='survey.user_input'

    def_mark_done(self):
        """Willaddcertificationtoemployee'sresuméif
        -Thesurveyisacertification
        -Theuserislinkedtoanemployee
        -Theusersucceededthetest"""

        super(SurveyUserInput,self)._mark_done()

        certification_user_inputs=self.filtered(lambdauser_input:user_input.survey_id.certificationanduser_input.scoring_success)
        partner_has_completed={user_input.partner_id.id:user_input.survey_idforuser_inputincertification_user_inputs}
        employees=self.env['hr.employee'].sudo().search([('user_id.partner_id','in',certification_user_inputs.mapped('partner_id').ids)])
        foremployeeinemployees:
            line_type=self.env.ref('hr_skills_survey.resume_type_certification',raise_if_not_found=False)
            survey=partner_has_completed.get(employee.user_id.partner_id.id)
            self.env['hr.resume.line'].create({
                'employee_id':employee.id,
                'name':survey.title,
                'date_start':fields.Date.today(),
                'date_end':fields.Date.today(),
                'description':html2plaintext(survey.description),
                'line_type_id':line_typeandline_type.id,
                'display_type':'certification',
                'survey_id':survey.id
            })


classResumeLine(models.Model):
    _inherit='hr.resume.line'

    display_type=fields.Selection(selection_add=[('certification','Certification')])
    survey_id=fields.Many2one('survey.survey',string='Certification',readonly=True)
