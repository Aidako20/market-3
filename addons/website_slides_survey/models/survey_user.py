#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api
fromflectra.osvimportexpression


classSurveyUserInput(models.Model):
    _inherit='survey.user_input'

    slide_id=fields.Many2one('slide.slide','Relatedcourseslide',
        help="Therelatedcourseslidewhenthereisnomembershipinformation")
    slide_partner_id=fields.Many2one('slide.slide.partner','Subscriberinformation',
        help="Slidemembershipinformationfortheloggedinuser")

    @api.model_create_multi
    defcreate(self,vals_list):
        records=super(SurveyUserInput,self).create(vals_list)
        records._check_for_failed_attempt()
        returnrecords

    defwrite(self,vals):
        res=super(SurveyUserInput,self).write(vals)
        if'state'invals:
            self._check_for_failed_attempt()
        returnres

    def_check_for_failed_attempt(self):
        """Iftheuserfailshislastattemptatacoursecertification,
        weremovehimfromthemembersofthecourse(andhehastoenrollagain).
        Hereceivesanemailintheprocessnotifyinghimofhisfailureandsuggesting
        heenrollstothecourseagain.

        Thepurposeistohavea'certificationflow'wheretheusercanre-purchasethe
        certificationwhentheyhavefailedit."""

        ifself:
            user_inputs=self.search([
                ('id','in',self.ids),
                ('state','=','done'),
                ('scoring_success','=',False),
                ('slide_partner_id','!=',False)
            ])

            ifuser_inputs:
                foruser_inputinuser_inputs:
                    removed_memberships_per_partner={}
                    ifuser_input.survey_id._has_attempts_left(user_input.partner_id,user_input.email,user_input.invite_token):
                        #skipifuserstillhasattemptsleft
                        continue

                    self.env.ref('website_slides_survey.mail_template_user_input_certification_failed').send_mail(
                        user_input.id,notif_layout="mail.mail_notification_light"
                    )

                    removed_memberships=removed_memberships_per_partner.get(
                        user_input.partner_id,
                        self.env['slide.channel']
                    )
                    removed_memberships|=user_input.slide_partner_id.channel_id
                    removed_memberships_per_partner[user_input.partner_id]=removed_memberships

                forpartner_id,removed_membershipsinremoved_memberships_per_partner.items():
                    removed_memberships._remove_membership(partner_id.ids)
