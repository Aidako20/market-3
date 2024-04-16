#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.survey.controllers.mainimportSurvey


classSurvey(Survey):
    def_prepare_survey_finished_values(self,survey,answer,token=False):
        result=super(Survey,self)._prepare_survey_finished_values(survey,answer,token)
        ifanswer.slide_id:
            result['channel_url']=answer.slide_id.channel_id.website_url

        returnresult

    def_prepare_retry_additional_values(self,answer):
        result=super(Survey,self)._prepare_retry_additional_values(answer)
        ifanswer.slide_id:
            result['slide_id']=answer.slide_id.id
        ifanswer.slide_partner_id:
            result['slide_partner_id']=answer.slide_partner_id.id

        returnresult
