#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importhashlib
importuuid

fromdatetimeimportdatetime
fromwerkzeugimporturls
fromflectraimportapi,models

VALIDATION_KARMA_GAIN=3


classUsers(models.Model):
    _inherit='res.users'

    def__init__(self,pool,cr):
        init_res=super(Users,self).__init__(pool,cr)
        pool[self._name].SELF_WRITEABLE_FIELDS=list(
            set(
                self.SELF_WRITEABLE_FIELDS+
                ['country_id','city','website','website_description','website_published']))
        pool[self._name].SELF_READABLE_FIELDS=pool[self._name].SELF_READABLE_FIELDS+['karma']
        returninit_res

    @api.model
    def_generate_profile_token(self,user_id,email):
        """Returnatokenforemailvalidation.Thistokenisvalidfortheday
        andisahashbasedona(secret)uuidgeneratedbytheforummodule,
        theuser_id,theemailandcurrentlytheday(tobeupdatedifnecessary)."""
        profile_uuid=self.env['ir.config_parameter'].sudo().get_param('website_profile.uuid')
        ifnotprofile_uuid:
            profile_uuid=str(uuid.uuid4())
            self.env['ir.config_parameter'].sudo().set_param('website_profile.uuid',profile_uuid)
        returnhashlib.sha256((u'%s-%s-%s-%s'%(
            datetime.now().replace(hour=0,minute=0,second=0,microsecond=0),
            profile_uuid,
            user_id,
            email
        )).encode('utf-8')).hexdigest()

    def_send_profile_validation_email(self,**kwargs):
        ifnotself.email:
            returnFalse
        token=self._generate_profile_token(self.id,self.email)
        activation_template=self.env.ref('website_profile.validation_email')
        ifactivation_template:
            params={
                'token':token,
                'user_id':self.id,
                'email':self.email
            }
            params.update(kwargs)
            base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            token_url=base_url+'/profile/validate_email?%s'%urls.url_encode(params)
            withself._cr.savepoint():
                activation_template.sudo().with_context(token_url=token_url).send_mail(
                    self.id,force_send=True,raise_exception=True)
        returnTrue

    def_process_profile_validation_token(self,token,email):
        self.ensure_one()
        validation_token=self._generate_profile_token(self.id,email)
        iftoken==validation_tokenandself.karma==0:
            returnself.write({'karma':VALIDATION_KARMA_GAIN})
        returnFalse
