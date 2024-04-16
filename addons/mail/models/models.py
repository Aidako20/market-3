#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromlxml.builderimportE

fromflectraimportapi,models,tools,_


classBaseModel(models.AbstractModel):
    _inherit='base'

    #------------------------------------------------------------
    #GENERICMAILFEATURES
    #------------------------------------------------------------

    def_mail_track(self,tracked_fields,initial):
        """Foragivenrecord,fieldstocheck(tuplecolumnname,columninfo)
        andinitialvalues,returnavalidcommandtocreatetrackingvalues.

        :paramtracked_fields:fields_getofupdatedfieldsonwhichtracking
          ischeckedandperformed;
        :paraminitial:dictofinitialvaluesforeachupdatedfields;

        :return:atuple(changes,tracking_value_ids)where
          changes:setofupdatedcolumnnames;
          tracking_value_ids:alistofORM(0,0,values)commandstocreate
          ``mail.tracking.value``records;

        Overridethismethodonaspecificmodeltoimplementmodel-specific
        behavior.Alsoconsiderinheritingfrom``mail.thread``."""
        self.ensure_one()
        changes=set() #containsonchangetrackedfieldsthatchanged
        tracking_value_ids=[]

        #generatetracked_valuesdatastructure:{'col_name':{col_info,new_value,old_value}}
        forcol_name,col_infointracked_fields.items():
            ifcol_namenotininitial:
                continue
            initial_value=initial[col_name]
            new_value=self[col_name]

            ifnew_value!=initial_valueand(new_valueorinitial_value): #becausebrowsenull!=False
                tracking_sequence=getattr(self._fields[col_name],'tracking',
                                            getattr(self._fields[col_name],'track_sequence',100)) #backwardcompatibilitywitholdparametername
                iftracking_sequenceisTrue:
                    tracking_sequence=100
                tracking=self.env['mail.tracking.value'].create_tracking_values(initial_value,new_value,col_name,col_info,tracking_sequence,self._name)
                iftracking:
                    tracking_value_ids.append([0,0,tracking])
                changes.add(col_name)

        returnchanges,tracking_value_ids

    def_message_get_default_recipients(self):
        """Genericimplementationforfindingdefaultrecipienttomailon
        arecordset.Thismethodisagenericimplementationavailablefor
        allmodelsaswecouldsendanemailthroughmailtemplatesonmodels
        notinheritingfrommail.thread.

        Overridethismethodonaspecificmodeltoimplementmodel-specific
        behavior.Alsoconsiderinheritingfrom``mail.thread``."""
        res={}
        forrecordinself:
            recipient_ids,email_to,email_cc=[],False,False
            if'partner_id'inrecordandrecord.partner_id:
                recipient_ids.append(record.partner_id.id)
            else:
                found_email=False
                if'email_from'inrecordandrecord.email_from:
                    found_email=record.email_from
                elif'partner_email'inrecordandrecord.partner_email:
                    found_email=record.partner_email
                elif'email'inrecordandrecord.email:
                    found_email=record.email
                elif'email_normalized'inrecordandrecord.email_normalized:
                    found_email=record.email_normalized
                iffound_email:
                    email_to=','.join(tools.email_normalize_all(found_email))
                ifnotemail_to: #keepvaluetoeasedebug/traceupdate
                    email_to=found_email
            res[record.id]={'partner_ids':recipient_ids,'email_to':email_to,'email_cc':email_cc}
        returnres

    def_notify_get_reply_to(self,default=None,records=None,company=None,doc_names=None):
        """Returnsthepreferredreply-toemailaddresswhenreplyingtoathread
        ondocuments.Thismethodisagenericimplementationavailablefor
        allmodelsaswecouldsendanemailthroughmailtemplatesonmodels
        notinheritingfrommail.thread.

        Reply-toisformattedlike"MyCompanyMyDocument<reply.to@domain>".
        Heuristicitthefollowing:
         *searchforspecificaliasesastheyalwayshavepriority;itislimited
           toaliaseslinkedtodocuments(likeprojectaliasfortaskforexample);
         *usecatchalladdress;
         *usedefault;

        Thismethodcanbeusedasagenerictoolsifselfisavoidrecordset.

        Overridethismethodonaspecificmodeltoimplementmodel-specific
        behavior.Alsoconsiderinheritingfrom``mail.thread``.
        Anexamplewouldbetaskstakingtheirreply-toaliasfromtheirproject.

        :paramdefault:defaultemailifnoaliasorcatchallisfound;
        :paramrecords:DEPRECATED,selfshouldbeavalidrecordsetoran
          emptyrecordsetifagenericreply-toisrequired;
        :paramcompany:usedtocomputecompanynamepartofthefromname;provide
          itifalreadyknown,otherwiseuserecordscompanyittheyallbelongtothesamecompany
          andfallbackonuser'scompanyinmixedcompaniesenvironments;
        :paramdoc_names:dict(res_id,doc_name)usedtocomputedocnamepartof
          thefromname;provideitifalreadyknowntoavoidqueries,otherwise
          name_getondocumentwillbeperformed;
        :returnresult:dictionary.KeysarerecordIDsandvalueisformatted
          likeanemail"Company_nameDocument_name<reply_to@email>"/
        """
        ifrecords:
            raiseValueError('UseofrecordsisdeprecatedasthismethodisavailableonBaseModel.')

        _records=self
        model=_records._nameif_recordsand_records._name!='mail.thread'elseFalse
        res_ids=_records.idsif_recordsandmodelelse[]
        _res_ids=res_idsor[False] #alwayshaveadefaultvaluelocatedinFalse

        alias_domain=self.env['ir.config_parameter'].sudo().get_param("mail.catchall.domain")
        result=dict.fromkeys(_res_ids,False)
        result_email=dict()
        doc_names=doc_namesifdoc_nameselsedict()

        ifalias_domain:
            ifmodelandres_ids:
                ifnotdoc_names:
                    doc_names=dict((rec.id,rec.display_name)forrecin_records)

                ifnotcompanyand'company_id'inselfandlen(self.company_id)==1:
                    company=self.company_id

                mail_aliases=self.env['mail.alias'].sudo().search([
                    ('alias_parent_model_id.model','=',model),
                    ('alias_parent_thread_id','in',res_ids),
                    ('alias_name','!=',False)])
                #takeonlyfirstfoundaliasforeachthread_id,tomatchorder(1found->limit=1foreachres_id)
                foraliasinmail_aliases:
                    result_email.setdefault(alias.alias_parent_thread_id,'%s@%s'%(alias.alias_name,alias_domain))

            #leftids:usecatchall
            left_ids=set(_res_ids)-set(result_email)
            ifleft_ids:
                catchall=self.env['ir.config_parameter'].sudo().get_param("mail.catchall.alias")
                ifcatchall:
                    result_email.update(dict((rid,'%s@%s'%(catchall,alias_domain))forridinleft_ids))

            forres_idinresult_email:
                result[res_id]=self._notify_get_reply_to_formatted_email(
                    result_email[res_id],
                    doc_names.get(res_id)or'',
                    company
                )

        left_ids=set(_res_ids)-set(result_email)
        ifleft_ids:
            result.update(dict((res_id,default)forres_idinleft_ids))

        returnresult

    def_notify_get_reply_to_formatted_email(self,record_email,record_name,company):
        """Computeformattedemailforreply_toandtrytoavoidrefoldissue
        withpythonthatsplitsthereply-toovermultiplelines.Itisdueto
        abadmanagementofquotes(missingquotesafterrefold).Thisappears
        thereforeonlywhenhavingquotes(akanotsimplenames,andnotwhen
        beingunicodeencoded).

        Toavoidthatissuewhenformataddrwouldreturnmorethan78charswe
        returnasimplifiedname/emailtotrytostayunder78chars.Ifnot
        possiblewereturnonlytheemailandskiptheformataddrwhichcauses
        theissueinpython.Wedonotusehackslikecropthenamepartas
        encodingandquotingwouldbeerrorprone.
        """
        #addressitselfistoolongfor78charslimit:returnonlyemail
        iflen(record_email)>=78:
            returnrecord_email

        company_name=company.nameifcompanyelseself.env.company.name

        #trycompany_name+record_name,orrecord_namealone(orcompany_namealone)
        name=f"{company_name}{record_name}"ifrecord_nameelsecompany_name

        formatted_email=tools.formataddr((name,record_email))
        iflen(formatted_email)>78:
            formatted_email=tools.formataddr((record_nameorcompany_name,record_email))
        iflen(formatted_email)>78:
            formatted_email=record_email
        returnformatted_email

    #------------------------------------------------------------
    #ALIASMANAGEMENT
    #------------------------------------------------------------

    def_alias_check_contact(self,message,message_dict,alias):
        """Deprecated,removeinv14+"""
        error_msg=self._alias_get_error_message(message,message_dict,alias)
        returnerror_msgiferror_msgelseTrue

    def_alias_get_error_message(self,message,message_dict,alias):
        """Genericmethodthattakesarecordnotnecessarilyinheritingfrom
        mail.alias.mixin."""
        author=self.env['res.partner'].browse(message_dict.get('author_id',False))
        ifalias.alias_contact=='followers':
            ifnotself.ids:
                return_('incorrectlyconfiguredalias(unknownreferencerecord)')
            ifnothasattr(self,"message_partner_ids")ornothasattr(self,"message_channel_ids"):
                return_('incorrectlyconfiguredalias')
            accepted_partner_ids=self.message_partner_ids|self.message_channel_ids.mapped('channel_partner_ids')
            ifnotauthororauthornotinaccepted_partner_ids:
                return_('restrictedtofollowers')
        elifalias.alias_contact=='partners'andnotauthor:
            return_('restrictedtoknownauthors')
        returnFalse

    #------------------------------------------------------------
    #ACTIVITY
    #------------------------------------------------------------

    @api.model
    def_get_default_activity_view(self):
        """Generatesanemptyactivityview.

        :returns:aactivityviewasanlxmldocument
        :rtype:etree._Element
        """
        field=E.field(name=self._rec_name_fallback())
        activity_box=E.div(field,{'t-name':"activity-box"})
        templates=E.templates(activity_box)
        returnE.activity(templates,string=self._description)

    #------------------------------------------------------------
    #GATEWAY:NOTIFICATION
    #------------------------------------------------------------

    def_notify_email_headers(self):
        """
            Generatetheemailheadersbasedonrecord
        """
        ifnotself:
            return{}
        self.ensure_one()
        returnrepr(self._notify_email_header_dict())

    def_notify_email_header_dict(self):
        return{
            'X-Flectra-Objects':"%s-%s"%(self._name,self.id),
        }
