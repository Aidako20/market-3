#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.httpimportrequest
fromflectra.addons.survey.controllers.mainimportSurvey


classRecruitmentSurvey(Survey):

    def_check_validity(self,survey_token,answer_token,ensure_token=True,check_partner=True):
        check_partner=check_partnerandnotrequest.env.user.has_group('hr_recruitment.group_hr_recruitment_user')
        returnsuper(RecruitmentSurvey,self)._check_validity(survey_token,answer_token,ensure_token,check_partner)
