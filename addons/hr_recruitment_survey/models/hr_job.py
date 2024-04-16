#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,_


classJob(models.Model):
    _inherit="hr.job"

    survey_id=fields.Many2one(
        'survey.survey',"InterviewForm",
        help="Chooseaninterviewformforthisjobpositionandyouwillbeabletoprint/answerthisinterviewfromallapplicantswhoapplyforthisjob")

    defaction_print_survey(self):
        returnself.survey_id.action_print_survey()

    defaction_new_survey(self):
        self.ensure_one()
        survey=self.env['survey.survey'].create({
            'title':_("InterviewForm:%s")%self.name,
        })
        self.write({'survey_id':survey.id})

        action={
                'name':_('Survey'),
                'view_mode':'form,tree',
                'res_model':'survey.survey',
                'type':'ir.actions.act_window',
                'context':{'form_view_initial_mode':'edit'},
                'res_id':survey.id,
            }

        returnaction
