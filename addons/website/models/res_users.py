#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importlogging

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError
fromflectra.httpimportrequest

_logger=logging.getLogger(__name__)


classResUsers(models.Model):
    _inherit='res.users'

    website_id=fields.Many2one('website',related='partner_id.website_id',store=True,related_sudo=False,readonly=False)

    _sql_constraints=[
        #Partialconstraint,complementedbyapythonconstraint(seebelow).
        ('login_key','unique(login,website_id)','Youcannothavetwouserswiththesamelogin!'),
    ]

    @api.constrains('login','website_id')
    def_check_login(self):
        """Donotallowtwouserswiththesameloginwithoutwebsite"""
        self.flush(['login','website_id'])
        self.env.cr.execute(
            """SELECTlogin
                 FROMres_users
                WHEREloginIN(SELECTloginFROMres_usersWHEREidIN%sANDwebsite_idISNULL)
                  ANDwebsite_idISNULL
             GROUPBYlogin
               HAVINGCOUNT(*)>1
            """,
            (tuple(self.ids),)
        )
        ifself.env.cr.rowcount:
            raiseValidationError(_('Youcannothavetwouserswiththesamelogin!'))

    @api.model
    def_get_login_domain(self,login):
        website=self.env['website'].get_current_website()
        returnsuper(ResUsers,self)._get_login_domain(login)+website.website_domain()

    @api.model
    def_get_email_domain(self,email):
        website=self.env['website'].get_current_website()
        returnsuper()._get_email_domain(email)+website.website_domain()

    @api.model
    def_get_login_order(self):
        return'website_id,'+super(ResUsers,self)._get_login_order()

    @api.model
    def_signup_create_user(self,values):
        current_website=self.env['website'].get_current_website()
        #Notethatforthemoment,portaluserscanconnecttoallwebsitesof
        #allcompaniesaslongasthespecific_user_accountsettingisnot
        #activated.
        values['company_id']=current_website.company_id.id
        values['company_ids']=[(4,current_website.company_id.id)]
        ifrequestandcurrent_website.specific_user_account:
            values['website_id']=current_website.id
        new_user=super(ResUsers,self)._signup_create_user(values)
        returnnew_user

    @api.model
    def_get_signup_invitation_scope(self):
        current_website=self.env['website'].get_current_website()
        returncurrent_website.auth_signup_uninvitedorsuper(ResUsers,self)._get_signup_invitation_scope()

    @classmethod
    defauthenticate(cls,db,login,password,user_agent_env):
        """Overridetolinktheloggedinuser'sres.partnertowebsite.visitor.
        Ifbotharequest-basedvisitorandauser-basedvisitorexistwetry
        toupdatethem(havesamepartner_id),andmovesubrecordstothemain
        visitor(userone).Purposeistotrytokeepamainvisitorwithas
        muchsub-records(trackedpages,leads,...)aspossible."""
        uid=super(ResUsers,cls).authenticate(db,login,password,user_agent_env)
        ifuid:
            withcls.pool.cursor()ascr:
                env=api.Environment(cr,uid,{})
                visitor_sudo=env['website.visitor']._get_visitor_from_request()
                ifvisitor_sudo:
                    user_partner=env.user.partner_id
                    other_user_visitor_sudo=env['website.visitor'].with_context(active_test=False).sudo().search(
                        [('partner_id','=',user_partner.id),('id','!=',visitor_sudo.id)],
                        order='last_connection_datetimeDESC',
                    ) #current13.3state:1resultmaxasuniquevisitor/partner
                    ifother_user_visitor_sudo:
                        visitor_main=other_user_visitor_sudo[0]
                        other_visitors=other_user_visitor_sudo[1:] #normallyvoid
                        (visitor_sudo+other_visitors)._link_to_visitor(visitor_main,keep_unique=True)
                        visitor_main.name=user_partner.name
                        visitor_main.active=True
                        visitor_main._update_visitor_last_visit()
                    else:
                        ifvisitor_sudo.partner_id!=user_partner:
                            visitor_sudo._link_to_partner(
                                user_partner,
                                update_values={'partner_id':user_partner.id})
                        visitor_sudo._update_visitor_last_visit()
        returnuid
