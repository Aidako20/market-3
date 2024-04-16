#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging

fromflectra.tools.translateimport_
fromflectra.toolsimportemail_split
fromflectra.exceptionsimportUserError

fromflectraimportapi,fields,models


_logger=logging.getLogger(__name__)

#welcomeemailsenttoportalusers
#(notethatcalling'_'hasnoeffectexceptexportingthosestringsfortranslation)

defextract_email(email):
    """extracttheemailaddressfromauser-friendlyemailaddress"""
    addresses=email_split(email)
    returnaddresses[0]ifaddresseselse''


classPortalWizard(models.TransientModel):
    """
        Awizardtomanagethecreation/removalofportalusers.
    """

    _name='portal.wizard'
    _description='GrantPortalAccess'

    def_default_user_ids(self):
        #foreachpartner,determinecorrespondingportal.wizard.userrecords
        partner_ids=self.env.context.get('active_ids',[])
        contact_ids=set()
        user_changes=[]
        forpartnerinself.env['res.partner'].sudo().browse(partner_ids):
            contact_partners=partner.child_ids.filtered(lambdap:p.typein('contact','other'))|partner
            forcontactincontact_partners:
                #makesurethateachcontactappearsatmostonceinthelist
                ifcontact.idnotincontact_ids:
                    contact_ids.add(contact.id)
                    in_portal=False
                    ifcontact.user_ids:
                        in_portal=self.env.ref('base.group_portal')incontact.user_ids[0].groups_id
                    user_changes.append((0,0,{
                        'partner_id':contact.id,
                        'email':contact.email,
                        'in_portal':in_portal,
                    }))
        returnuser_changes

    user_ids=fields.One2many('portal.wizard.user','wizard_id',string='Users',default=_default_user_ids)
    welcome_message=fields.Text('InvitationMessage',help="Thistextisincludedintheemailsenttonewusersoftheportal.")

    defaction_apply(self):
        self.ensure_one()
        self.user_ids.action_apply()
        return{'type':'ir.actions.act_window_close'}


classPortalWizardUser(models.TransientModel):
    """
        Amodeltoconfigureusersintheportalwizard.
    """

    _name='portal.wizard.user'
    _description='PortalUserConfig'

    wizard_id=fields.Many2one('portal.wizard',string='Wizard',required=True,ondelete='cascade')
    partner_id=fields.Many2one('res.partner',string='Contact',required=True,readonly=True,ondelete='cascade')
    email=fields.Char('Email')
    in_portal=fields.Boolean('InPortal')
    user_id=fields.Many2one('res.users',string='LoginUser')

    defget_error_messages(self):
        emails=[]
        partners_error_empty=self.env['res.partner']
        partners_error_emails=self.env['res.partner']
        partners_error_user=self.env['res.partner']
        partners_error_internal_user=self.env['res.partner']

        forwizard_userinself.with_context(active_test=False).filtered(lambdaw:w.in_portalandnotw.partner_id.user_ids):
            email=extract_email(wizard_user.email)
            ifnotemail:
                partners_error_empty|=wizard_user.partner_id
            elifemailinemails:
                partners_error_emails|=wizard_user.partner_id
            user=self.env['res.users'].sudo().with_context(active_test=False).search([('login','=ilike',email)])
            ifuser:
                partners_error_user|=wizard_user.partner_id
            emails.append(email)

        forwizard_userinself.with_context(active_test=False):
            ifany(u.has_group('base.group_user')foruinwizard_user.sudo().partner_id.user_ids):
                partners_error_internal_user|=wizard_user.partner_id

        error_msg=[]
        ifpartners_error_empty:
            error_msg.append("%s\n-%s"%(_("Somecontactsdon'thaveavalidemail:"),
                                '\n-'.join(partners_error_empty.mapped('display_name'))))
        ifpartners_error_emails:
            error_msg.append("%s\n-%s"%(_("Severalcontactshavethesameemail:"),
                                '\n-'.join(partners_error_emails.mapped('email'))))
        ifpartners_error_user:
            error_msg.append("%s\n-%s"%(_("Somecontactshavethesameemailasanexistingportaluser:"),
                                '\n-'.join([p.email_formattedforpinpartners_error_user])))
        ifpartners_error_internal_user:
            error_msg.append("%s\n-%s"%(_("Somecontactsarealreadyinternalusers:"),
                                '\n-'.join(partners_error_internal_user.mapped('email'))))
        iferror_msg:
            error_msg.append(_("Toresolvethiserror,youcan:\n"
                "-Correcttheemailsoftherelevantcontacts\n"
                "-Grantaccessonlytocontactswithuniqueemails"))
            error_msg[-1]+=_("\n-Switchtheinternaluserstoportalmanually")
        returnerror_msg

    defaction_apply(self):
        self.env['res.partner'].check_access_rights('write')
        """Fromselectedpartners,addcorrespondinguserstochosenportalgroup.Iteithergranted
            existinguser,orcreatenewone(andaddittothegroup).
        """
        error_msg=self.get_error_messages()
        iferror_msg:
            raiseUserError("\n\n".join(error_msg))

        forwizard_userinself.sudo().with_context(active_test=False):

            group_portal=self.env.ref('base.group_portal')
            #Checkingifthepartnerhasalinkeduser
            user=wizard_user.partner_id.user_ids[0]ifwizard_user.partner_id.user_idselseNone
            #updatepartneremail,ifanewonewasintroduced
            ifwizard_user.partner_id.email!=wizard_user.email:
                wizard_user.partner_id.write({'email':wizard_user.email})
            #addportalgrouptorelativeuserofselectedpartners
            ifwizard_user.in_portal:
                user_portal=None
                #createauserifnecessary,andmakesureitisintheportalgroup
                ifnotuser:
                    ifwizard_user.partner_id.company_id:
                        company_id=wizard_user.partner_id.company_id.id
                    else:
                        company_id=self.env.company.id
                    user_portal=wizard_user.sudo().with_company(company_id)._create_user()
                else:
                    user_portal=user
                wizard_user.write({'user_id':user_portal.id})
                ifnotwizard_user.user_id.activeorgroup_portalnotinwizard_user.user_id.groups_id:
                    wizard_user.user_id.write({'active':True,'groups_id':[(4,group_portal.id)]})
                    #prepareforthesignupprocess
                    wizard_user.user_id.partner_id.signup_prepare()
                wizard_user.with_context(active_test=True)._send_email()
                wizard_user.refresh()
            else:
                #removetheuser(ifitexists)fromtheportalgroup
                ifuserandgroup_portalinuser.groups_id:
                    #ifuserbelongstoportalonly,deactivateit
                    iflen(user.groups_id)<=1:
                        user.write({'groups_id':[(3,group_portal.id)],'active':False})
                    else:
                        user.write({'groups_id':[(3,group_portal.id)]})

    def_create_user(self):
        """createanewuserforwizard_user.partner_id
            :returnsrecordofres.users
        """
        returnself.env['res.users'].with_context(no_reset_password=True)._create_user_from_template({
            'email':extract_email(self.email),
            'login':extract_email(self.email),
            'partner_id':self.partner_id.id,
            'company_id':self.env.company.id,
            'company_ids':[(6,0,self.env.company.ids)],
        })

    def_send_email(self):
        """sendnotificationemailtoanewportaluser"""
        ifnotself.env.user.email:
            raiseUserError(_('YoumusthaveanemailaddressinyourUserPreferencestosendemails.'))

        #determinesubjectandbodyintheportaluser'slanguage
        template=self.env.ref('portal.mail_template_data_portal_welcome')
        forwizard_lineinself:
            lang=wizard_line.user_id.lang
            partner=wizard_line.user_id.partner_id

            portal_url=partner.with_context(signup_force_type_in_url='',lang=lang)._get_signup_url_for_action()[partner.id]
            partner.signup_prepare()

            iftemplate:
                template.with_context(dbname=self._cr.dbname,portal_url=portal_url,lang=lang).send_mail(wizard_line.id,force_send=True)
            else:
                _logger.warning("Noemailtemplatefoundforsendingemailtotheportaluser")

        returnTrue
