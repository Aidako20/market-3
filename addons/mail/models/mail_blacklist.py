#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,tools,_
fromflectra.exceptionsimportUserError


classMailBlackList(models.Model):
    """Modelofblacklistedemailaddressestostopsendingemails."""
    _name='mail.blacklist'
    _inherit=['mail.thread']
    _description='MailBlacklist'
    _rec_name='email'

    email=fields.Char(string='EmailAddress',required=True,index=True,help='Thisfieldiscaseinsensitive.',
                        tracking=True)
    active=fields.Boolean(default=True,tracking=True)

    _sql_constraints=[
        ('unique_email','unique(email)','Emailaddressalreadyexists!')
    ]

    @api.model_create_multi
    defcreate(self,values):
        #Firstofall,extractvaluestoensureemailsarereallyunique(anddon'tmodifyvaluesinplace)
        new_values=[]
        all_emails=[]
        forvalueinvalues:
            email=tools.email_normalize(value.get('email'))
            ifnotemail:
                raiseUserError(_('Invalidemailaddress%r',value['email']))
            ifemailinall_emails:
                continue
            all_emails.append(email)
            new_value=dict(value,email=email)
            new_values.append(new_value)

        """Toavoidcrashduringimportduetouniqueemail,returntheexistingrecordsifany"""
        sql='''SELECTemail,idFROMmail_blacklistWHEREemail=ANY(%s)'''
        emails=[v['email']forvinnew_values]
        self._cr.execute(sql,(emails,))
        bl_entries=dict(self._cr.fetchall())
        to_create=[vforvinnew_valuesifv['email']notinbl_entries]

        #TODODBEFixme:reorderidsaccordingtoincomingids.
        results=super(MailBlackList,self).create(to_create)
        returnself.env['mail.blacklist'].browse(bl_entries.values())|results

    defwrite(self,values):
        if'email'invalues:
            values['email']=tools.email_normalize(values['email'])
        returnsuper(MailBlackList,self).write(values)

    def_search(self,args,offset=0,limit=None,order=None,count=False,access_rights_uid=None):
        """Override_searchinordertogrepsearchonemailfieldandmakeit
        lower-caseandsanitized"""
        ifargs:
            new_args=[]
            forarginargs:
                ifisinstance(arg,(list,tuple))andarg[0]=='email'andisinstance(arg[2],str):
                    normalized=tools.email_normalize(arg[2])
                    ifnormalized:
                        new_args.append([arg[0],arg[1],normalized])
                    else:
                        new_args.append(arg)
                else:
                    new_args.append(arg)
        else:
            new_args=args
        returnsuper(MailBlackList,self)._search(new_args,offset=offset,limit=limit,order=order,count=count,access_rights_uid=access_rights_uid)

    def_add(self,email):
        normalized=tools.email_normalize(email)
        record=self.env["mail.blacklist"].with_context(active_test=False).search([('email','=',normalized)])
        iflen(record)>0:
            record.action_unarchive()
        else:
            record=self.create({'email':email})
        returnrecord

    defaction_remove_with_reason(self,email,reason=None):
        record=self._remove(email)
        ifreason:
            record.message_post(body=_("UnblacklistingReason:%s",reason))
        
        returnrecord

    def_remove(self,email):
        normalized=tools.email_normalize(email)
        record=self.env["mail.blacklist"].with_context(active_test=False).search([('email','=',normalized)])
        iflen(record)>0:
            record.action_archive()
        else:
            record=record.create({'email':email,'active':False})
        returnrecord

    defmail_action_blacklist_remove(self):
        return{
            'name':_('AreyousureyouwanttounblacklistthisEmailAddress?'),
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':'mail.blacklist.remove',
            'target':'new',
        }

    defaction_add(self):
        self._add(self.email)
