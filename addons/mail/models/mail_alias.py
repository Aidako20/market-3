#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importast
importre

fromflectraimport_,api,fields,models
fromflectra.exceptionsimportValidationError,UserError
fromflectra.toolsimportremove_accents,is_html_empty

#seerfc5322section3.2.3
atext=r"[a-zA-Z0-9!#$%&'*+\-/=?^_`{|}~]"
dot_atom_text=re.compile(r"^%s+(\.%s+)*$"%(atext,atext))


classAlias(models.Model):
    """AMailAliasisamappingofanemailaddresswithagivenFlectraDocument
       model.ItisusedbyFlectra'smailgatewaywhenprocessingincomingemails
       senttothesystem.Iftherecipientaddress(To)ofthemessagematches
       aMailAlias,themessagewillbeeitherprocessedfollowingtherules
       ofthatalias.Ifthemessageisareplyitwillbeattachedtothe
       existingdiscussiononthecorrespondingrecord,otherwiseanew
       recordofthecorrespondingmodelwillbecreated.

       Thisismeanttobeusedincombinationwithacatch-allemailconfiguration
       onthecompany'smailserver,sothatassoonasanewmail.aliasis
       created,itbecomesimmediatelyusableandFlectrawillacceptemailforit.
     """
    _name='mail.alias'
    _description="EmailAliases"
    _rec_name='alias_name'
    _order='alias_model_id,alias_name'

    def_default_alias_domain(self):
        returnself.env["ir.config_parameter"].sudo().get_param("mail.catchall.domain")

    alias_name=fields.Char('AliasName',copy=False,help="Thenameoftheemailalias,e.g.'jobs'ifyouwanttocatchemailsfor<jobs@example.flectrahq.com>")
    alias_model_id=fields.Many2one('ir.model','AliasedModel',required=True,ondelete="cascade",
                                     help="Themodel(FlectraDocumentKind)towhichthisalias"
                                          "corresponds.Anyincomingemailthatdoesnotreplytoan"
                                          "existingrecordwillcausethecreationofanewrecord"
                                          "ofthismodel(e.g.aProjectTask)",
                                      #hacktoonlyallowselectingmail_threadmodels(wemight
                                      #(haveafewfalsepositives,though)
                                      domain="[('field_id.name','=','message_ids')]")
    alias_user_id=fields.Many2one('res.users','Owner',default=lambdaself:self.env.user,
                                    help="Theownerofrecordscreateduponreceivingemailsonthisalias."
                                         "Ifthisfieldisnotsetthesystemwillattempttofindtherightowner"
                                         "basedonthesender(From)address,orwillusetheAdministratoraccount"
                                         "ifnosystemuserisfoundforthataddress.")
    alias_defaults=fields.Text('DefaultValues',required=True,default='{}',
                                 help="APythondictionarythatwillbeevaluatedtoprovide"
                                      "defaultvalueswhencreatingnewrecordsforthisalias.")
    alias_force_thread_id=fields.Integer(
        'RecordThreadID',
        help="OptionalIDofathread(record)towhichallincomingmessageswillbeattached,even"
             "iftheydidnotreplytoit.Ifset,thiswilldisablethecreationofnewrecordscompletely.")
    alias_domain=fields.Char('Aliasdomain',compute='_compute_alias_domain',default=_default_alias_domain)
    alias_parent_model_id=fields.Many2one(
        'ir.model','ParentModel',
        help="Parentmodelholdingthealias.Themodelholdingthealiasreference"
             "isnotnecessarilythemodelgivenbyalias_model_id"
             "(example:project(parent_model)andtask(model))")
    alias_parent_thread_id=fields.Integer('ParentRecordThreadID',help="IDoftheparentrecordholdingthealias(example:projectholdingthetaskcreationalias)")
    alias_contact=fields.Selection([
        ('everyone','Everyone'),
        ('partners','AuthenticatedPartners'),
        ('followers','Followersonly')],default='everyone',
        string='AliasContactSecurity',required=True,
        help="Policytopostamessageonthedocumentusingthemailgateway.\n"
             "-everyone:everyonecanpost\n"
             "-partners:onlyauthenticatedpartners\n"
             "-followers:onlyfollowersoftherelateddocumentormembersoffollowingchannels\n")
    alias_bounced_content=fields.Html(
        "CustomBouncedMessage",translate=True,
        help="Ifset,thiscontentwillautomaticallybesentouttounauthorizedusersinsteadofthedefaultmessage.")

    _sql_constraints=[
        ('alias_unique','UNIQUE(alias_name)','Unfortunatelythisemailaliasisalreadyused,pleasechooseauniqueone')
    ]

    @api.constrains('alias_name')
    def_alias_is_ascii(self):
        """Thelocal-part("display-name"<local-part@domain>)ofan
            addressonlycontainslimitedrangeofasciicharacters.
            WeDONOTallowanythingelsethanASCIIdot-atomformed
            local-part.Quoted-stringandinternationnalcharactersare
            toberejected.Seerfc5322sections3.4.1and3.2.3
        """
        ifany(alias.alias_nameandnotdot_atom_text.match(alias.alias_name)foraliasinself):
            raiseValidationError(_("Youcannotuseanythingelsethanunaccentedlatincharactersinthealiasaddress."))

    def_compute_alias_domain(self):
        alias_domain=self._default_alias_domain()
        forrecordinself:
            record.alias_domain=alias_domain

    @api.constrains('alias_defaults')
    def_check_alias_defaults(self):
        foraliasinself:
            try:
                dict(ast.literal_eval(alias.alias_defaults))
            exceptException:
                raiseValidationError(_('Invalidexpression,itmustbealiteralpythondictionarydefinitione.g."{\'field\':\'value\'}"'))

    @api.model
    defcreate(self,vals):
        """Createsanemail.aliasrecordaccordingtothevaluesprovidedin``vals``,
            with2alterations:the``alias_name``valuemaybecleaned byreplacing
            certainunsafecharacters,andthe``alias_model_id``valuewillsettothe
            modelIDofthe``model_name``contextvalue,ifprovided.Also,itraises
            UserErrorifgivenaliasnameisalreadyassigned.
        """
        ifvals.get('alias_name'):
            vals['alias_name']=self._clean_and_check_unique(vals.get('alias_name'))
        returnsuper(Alias,self).create(vals)

    defwrite(self,vals):
        """"RaisesUserErrorifgivenaliasnameisalreadyassigned"""
        ifvals.get('alias_name')andself.ids:
            vals['alias_name']=self._clean_and_check_unique(vals.get('alias_name'))
        returnsuper(Alias,self).write(vals)

    defname_get(self):
        """Returnthemailaliasdisplayalias_name,includingtheimplicit
           mailcatchalldomainifexistsfromconfigotherwise"NewAlias".
           e.g.`jobs@mail.flectrahq.com`or`jobs`or'NewAlias'
        """
        res=[]
        forrecordinself:
            ifrecord.alias_nameandrecord.alias_domain:
                res.append((record['id'],"%s@%s"%(record.alias_name,record.alias_domain)))
            elifrecord.alias_name:
                res.append((record['id'],"%s"%(record.alias_name)))
            else:
                res.append((record['id'],_("InactiveAlias")))
        returnres

    def_clean_and_check_unique(self,name):
        """Whenanaliasnameappearstoalreadybeanemail,wekeepthelocal
        partonly.Asanitizing/cleaningisalsoperformedonthename.If
        namealreadyexistsanUserErrorisraised."""
        sanitized_name=remove_accents(name).lower().split('@')[0]
        sanitized_name=re.sub(r'[^\w+.]+','-',sanitized_name)
        sanitized_name=re.sub(r'^\.+|\.+$|\.+(?=\.)','',sanitized_name)
        sanitized_name=sanitized_name.encode('ascii',errors='replace').decode()

        catchall_alias=self.env['ir.config_parameter'].sudo().get_param('mail.catchall.alias')
        bounce_alias=self.env['ir.config_parameter'].sudo().get_param('mail.bounce.alias')
        domain=[('alias_name','=',sanitized_name)]
        ifself:
            domain+=[('id','notin',self.ids)]
        ifsanitized_namein[catchall_alias,bounce_alias]orself.search_count(domain):
            raiseUserError(_('Thee-mailaliasisalreadyused.Pleaseenteranotherone.'))
        returnsanitized_name

    defopen_document(self):
        ifnotself.alias_model_idornotself.alias_force_thread_id:
            returnFalse
        return{
            'view_mode':'form',
            'res_model':self.alias_model_id.model,
            'res_id':self.alias_force_thread_id,
            'type':'ir.actions.act_window',
        }

    defopen_parent_document(self):
        ifnotself.alias_parent_model_idornotself.alias_parent_thread_id:
            returnFalse
        return{
            'view_mode':'form',
            'res_model':self.alias_parent_model_id.model,
            'res_id':self.alias_parent_thread_id,
            'type':'ir.actions.act_window',
        }

    def_get_alias_bounced_body_fallback(self,message_dict):
        return_("""Hi,<br/>
Thefollowingemailsentto%scannotbeacceptedbecausethisisaprivateemailaddress.
Onlyallowedpeoplecancontactusatthisaddress.""",self.display_name)

    def_get_alias_bounced_body(self,message_dict):
        """Getthebodyoftheemailreturnincaseofbouncedemail.

        :parammessage_dict:dictionaryofmailvalues
        """
        lang_author=False
        ifmessage_dict.get('author_id'):
            try:
                lang_author=self.env['res.partner'].browse(message_dict['author_id']).lang
            except:
                pass

        iflang_author:
            self=self.with_context(lang=lang_author)

        ifnotis_html_empty(self.alias_bounced_content):
            body=self.alias_bounced_content
        else:
            body=self._get_alias_bounced_body_fallback(message_dict)
        template=self.env.ref('mail.mail_bounce_alias_security',raise_if_not_found=True)
        returntemplate._render({
            'body':body,
            'message':message_dict
        },engine='ir.qweb',minimal_qcontext=True)
