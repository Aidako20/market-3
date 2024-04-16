#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classSlidePartnerRelation(models.Model):
    _inherit='slide.slide.partner'

    user_input_ids=fields.One2many('survey.user_input','slide_partner_id','Certificationattempts')
    survey_scoring_success=fields.Boolean('CertificationSucceeded',compute='_compute_survey_scoring_success',store=True)

    @api.depends('partner_id','user_input_ids.scoring_success')
    def_compute_survey_scoring_success(self):
        succeeded_user_inputs=self.env['survey.user_input'].sudo().search([
            ('slide_partner_id','in',self.ids),
            ('scoring_success','=',True)
        ])
        succeeded_slide_partners=succeeded_user_inputs.mapped('slide_partner_id')
        forrecordinself:
            record.survey_scoring_success=recordinsucceeded_slide_partners

    def_compute_field_value(self,field):
        super()._compute_field_value(field)
        iffield.name=='survey_scoring_success':
            self.filtered('survey_scoring_success').write({
                'completed':True
            })

classSlide(models.Model):
    _inherit='slide.slide'

    slide_type=fields.Selection(selection_add=[
        ('certification','Certification')
    ],ondelete={'certification':'setdefault'})
    survey_id=fields.Many2one('survey.survey','Certification')
    nbr_certification=fields.Integer("NumberofCertifications",compute='_compute_slides_statistics',store=True)

    _sql_constraints=[
        ('check_survey_id',"CHECK(slide_type!='certification'ORsurvey_idISNOTNULL)","Aslideoftype'certification'requiresacertification."),
        ('check_certification_preview',"CHECK(slide_type!='certification'ORis_preview=False)","Aslideoftypecertificationcannotbepreviewed."),
    ]

    @api.onchange('survey_id')
    def_on_change_survey_id(self):
        ifself.survey_id:
            self.slide_type='certification'

    @api.model
    defcreate(self,values):
        rec=super(Slide,self).create(values)
        ifrec.survey_id:
            rec.slide_type='certification'
        if'survey_id'invalues:
            rec._ensure_challenge_category()
        returnrec

    defwrite(self,values):
        old_surveys=self.mapped('survey_id')
        result=super(Slide,self).write(values)
        if'survey_id'invalues:
            self._ensure_challenge_category(old_surveys=old_surveys-self.mapped('survey_id'))
        returnresult

    defunlink(self):
        old_surveys=self.mapped('survey_id')
        result=super(Slide,self).unlink()
        self._ensure_challenge_category(old_surveys=old_surveys,unlink=True)
        returnresult

    def_ensure_challenge_category(self,old_surveys=None,unlink=False):
        """Ifaslideislinkedtoasurveythatgivesabadge,thechallengecategoryofthisbadgemustbe
        setto'slides'inordertoappearunderthecertificationbadgelistonranks_badgespage.
        Ifthesurveyisunlinkedfromtheslide,thechallengecategorymustberesetto'certification'"""
        ifold_surveys:
            old_certification_challenges=old_surveys.mapped('certification_badge_id').challenge_ids
            old_certification_challenges.write({'challenge_category':'certification'})
        ifnotunlink:
            certification_challenges=self.mapped('survey_id').mapped('certification_badge_id').challenge_ids
            certification_challenges.write({'challenge_category':'slides'})

    def_generate_certification_url(self):
        """getamapofcertificationurlforcertificationslidefrom`self`.Theurlwillcomefromthesurveyuserinput:
                1/existingandnotdoneuser_inputformemberofthecourse
                2/createanewuser_inputformember
                3/fornomember,atestuser_inputiscreatedandtheurlisreturned
            Note:theslide.slides.partnershouldalreadyexist

            Wehavetogenerateanewinvite_tokentodifferentiatepoolsofattemptssincethe
            coursecanbeenrolledmultipletimes.
        """
        certification_urls={}
        forslideinself.filtered(lambdaslide:slide.slide_type=='certification'andslide.survey_id):
            ifslide.channel_id.is_member:
                user_membership_id_sudo=slide.user_membership_id.sudo()
                ifuser_membership_id_sudo.user_input_ids:
                    last_user_input=next(user_inputforuser_inputinuser_membership_id_sudo.user_input_ids.sorted(
                        lambdauser_input:user_input.create_date,reverse=True
                    ))
                    certification_urls[slide.id]=last_user_input.get_start_url()
                else:
                    user_input=slide.survey_id.sudo()._create_answer(
                        partner=self.env.user.partner_id,
                        check_attempts=False,
                        **{
                            'slide_id':slide.id,
                            'slide_partner_id':user_membership_id_sudo.id
                        },
                        invite_token=self.env['survey.user_input']._generate_invite_token()
                    )
                    certification_urls[slide.id]=user_input.get_start_url()
            else:
                user_input=slide.survey_id.sudo()._create_answer(
                    partner=self.env.user.partner_id,
                    check_attempts=False,
                    test_entry=True,**{
                        'slide_id':slide.id
                    }
                )
                certification_urls[slide.id]=user_input.get_start_url()
        returncertification_urls
