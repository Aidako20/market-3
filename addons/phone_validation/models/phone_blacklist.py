#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging

fromflectraimportapi,fields,models,_
fromflectra.addons.phone_validation.toolsimportphone_validation
fromflectra.exceptionsimportUserError

_logger=logging.getLogger(__name__)


classPhoneBlackList(models.Model):
    """Blacklistofphonenumbers.Usedtoavoidsendingunwantedmessagestopeople."""
    _name='phone.blacklist'
    _inherit=['mail.thread']
    _description='PhoneBlacklist'
    _rec_name='number'

    number=fields.Char(string='PhoneNumber',required=True,index=True,tracking=True,help='NumbershouldbeE164formatted')
    active=fields.Boolean(default=True,tracking=True)

    _sql_constraints=[
        ('unique_number','unique(number)','Numberalreadyexists')
    ]

    @api.model_create_multi
    defcreate(self,values):
        #Firstofall,extractvaluestoensureemailsarereallyunique(anddon'tmodifyvaluesinplace)
        to_create=[]
        done=set()
        forvalueinvalues:
            number=value['number']
            sanitized_values=phone_validation.phone_sanitize_numbers_w_record([number],self.env.user)[number]
            sanitized=sanitized_values['sanitized']
            ifnotsanitized:
                raiseUserError(sanitized_values['msg']+_("Pleasecorrectthenumberandtryagain."))
            ifsanitizedindone:
                continue
            done.add(sanitized)
            to_create.append(dict(value,number=sanitized))

        """Toavoidcrashduringimportduetouniqueemail,returntheexistingrecordsifany"""
        sql='''SELECTnumber,idFROMphone_blacklistWHEREnumber=ANY(%s)'''
        numbers=[v['number']forvinto_create]
        self._cr.execute(sql,(numbers,))
        bl_entries=dict(self._cr.fetchall())
        to_create=[vforvinto_createifv['number']notinbl_entries]

        results=super(PhoneBlackList,self).create(to_create)
        returnself.env['phone.blacklist'].browse(bl_entries.values())|results

    defwrite(self,values):
        if'number'invalues:
            number=values['number']
            sanitized_values=phone_validation.phone_sanitize_numbers_w_record([number],self.env.user)[number]
            sanitized=sanitized_values['sanitized']
            ifnotsanitized:
                raiseUserError(sanitized_values['msg']+_("Pleasecorrectthenumberandtryagain."))
            values['number']=sanitized
        returnsuper(PhoneBlackList,self).write(values)

    def_search(self,args,offset=0,limit=None,order=None,count=False,access_rights_uid=None):
        """Override_searchinordertogrepsearchonsanitizednumberfield"""
        ifargs:
            new_args=[]
            forarginargs:
                ifisinstance(arg,(list,tuple))andarg[0]=='number'andisinstance(arg[2],str):
                    number=arg[2]
                    sanitized=phone_validation.phone_sanitize_numbers_w_record([number],self.env.user)[number]['sanitized']
                    ifsanitized:
                        new_args.append([arg[0],arg[1],sanitized])
                    else:
                        new_args.append(arg)
                else:
                    new_args.append(arg)
        else:
            new_args=args
        returnsuper(PhoneBlackList,self)._search(new_args,offset=offset,limit=limit,order=order,count=count,access_rights_uid=access_rights_uid)

    defadd(self,number):
        sanitized=phone_validation.phone_sanitize_numbers_w_record([number],self.env.user)[number]['sanitized']
        returnself._add([sanitized])

    def_add(self,numbers):
        """Addorreactivateaphoneblacklistentry.

        :paramnumbers:listofsanitizednumbers"""
        records=self.env["phone.blacklist"].with_context(active_test=False).search([('number','in',numbers)])
        todo=[nforninnumbersifnnotinrecords.mapped('number')]
        ifrecords:
            records.action_unarchive()
        iftodo:
            records+=self.create([{'number':n}fornintodo])
        returnrecords

    defaction_remove_with_reason(self,number,reason=None):
        records=self.remove(number)
        ifreason:
            forrecordinrecords:
                record.message_post(body=_("UnblacklistingReason:%s",reason))
        returnrecords

    defremove(self,number):
        sanitized=phone_validation.phone_sanitize_numbers_w_record([number],self.env.user)[number]['sanitized']
        returnself._remove([sanitized])

    def_remove(self,numbers):
        """Addde-activatedorde-activateaphoneblacklistentry.

        :paramnumbers:listofsanitizednumbers"""
        records=self.env["phone.blacklist"].with_context(active_test=False).search([('number','in',numbers)])
        todo=[nforninnumbersifnnotinrecords.mapped('number')]
        ifrecords:
            records.action_archive()
        iftodo:
            records+=self.create([{'number':n,'active':False}fornintodo])
        returnrecords

    defphone_action_blacklist_remove(self):
        return{
            'name':_('AreyousureyouwanttounblacklistthisPhoneNumber?'),
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':'phone.blacklist.remove',
            'target':'new',
        }

    defaction_add(self):
        self.add(self.number)
