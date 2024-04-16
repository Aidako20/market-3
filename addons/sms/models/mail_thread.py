#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging

fromflectraimportapi,models,fields
fromflectra.addons.phone_validation.toolsimportphone_validation
fromflectra.toolsimporthtml2plaintext,plaintext2html

_logger=logging.getLogger(__name__)


classMailThread(models.AbstractModel):
    _inherit='mail.thread'

    message_has_sms_error=fields.Boolean(
        'SMSDeliveryerror',compute='_compute_message_has_sms_error',search='_search_message_has_sms_error',
        help="Ifchecked,somemessageshaveadeliveryerror.")

    def_compute_message_has_sms_error(self):
        res={}
        ifself.ids:
            self._cr.execute("""SELECTmsg.res_id,COUNT(msg.res_id)FROMmail_messagemsg
                                 RIGHTJOINmail_message_res_partner_needaction_relrel
                                 ONrel.mail_message_id=msg.idANDrel.notification_type='sms'ANDrel.notification_statusin('exception')
                                 WHEREmsg.author_id=%sANDmsg.model=%sANDmsg.res_idin%sANDmsg.message_type!='user_notification'
                                 GROUPBYmsg.res_id""",
                             (self.env.user.partner_id.id,self._name,tuple(self.ids),))
            res.update(self._cr.fetchall())

        forrecordinself:
            record.message_has_sms_error=bool(res.get(record._origin.id,0))

    @api.model
    def_search_message_has_sms_error(self,operator,operand):
        return['&',('message_ids.has_sms_error',operator,operand),('message_ids.author_id','=',self.env.user.partner_id.id)]

    def_sms_get_partner_fields(self):
        """Thismethodreturnsthefieldstousetofindthecontacttolink
        whensendinganSMS.Havingpartnerisnotnecessary,havingonlyphone
        numberfieldsispossible.Howeveritgivesmoreflexibilityto
        notificationsmanagementwhenhavingpartners."""
        fields=[]
        ifhasattr(self,'partner_id'):
            fields.append('partner_id')
        ifhasattr(self,'partner_ids'):
            fields.append('partner_ids')
        returnfields

    def_sms_get_default_partners(self):
        """Thismethodwilllikelyneedtobeoverriddenbyinheritedmodels.
               :returnspartners:recordsetofres.partner
        """
        partners=self.env['res.partner']
        forfnameinself._sms_get_partner_fields():
            partners=partners.union(*self.mapped(fname)) #ensureordering
        returnpartners

    def_sms_get_number_fields(self):
        """Thismethodreturnsthefieldstousetofindthenumbertouseto
        sendanSMSonarecord."""
        if'mobile'inself:
            return['mobile']
        return[]

    def_sms_get_recipients_info(self,force_field=False,partner_fallback=True):
        """"GetSMSrecipientinformationoncurrentrecordset.Thismethod
        checksfornumbersandsanitationinordertocentralizecomputation.

        Exampleofusecases

          *clickonafield->numberisactuallyforcedfromfield,findcustomer
            linkedtorecord,forceitsnumbertofieldorfallbackoncustomerfields;
          *contact->findnumbersfromallpossiblephonefieldsonrecord,find
            customer,forceitsnumbertofoundfieldnumberorfallbackoncustomerfields;

        :paramforce_field:eithergiveaspecificfieldtofindphonenumber,either
            genericheuristicisusedtofindonebasedon``_sms_get_number_fields``;
        :parampartner_fallback:ifnovaluefoundintherecord,checkitscustomer
            valuesbasedon``_sms_get_default_partners``;

        :returndict:record.id:{
            'partner':ares.partnerrecordsetthatisthecustomer(voidorsingleton)
                linkedtotherecipient.See``_sms_get_default_partners``;
            'sanitized':sanitizednumbertouse(comingfromrecord'sfieldorpartner's
                phonefields).SettoFalseisnumberimpossibletoparseandformat;
            'number':originalnumberbeforesanitation;
            'partner_store':whetherthenumbercomesfromthecustomerphonefields.If
                Falseitmeansnumbercomesfromtherecorditself,eveniflinkedtoa
                customer;
            'field_store':fieldinwhichthenumberhasbeenfound(generallymobileor
                phone,see``_sms_get_number_fields``);
        }foreachrecordinself
        """
        result=dict.fromkeys(self.ids,False)
        tocheck_fields=[force_field]ifforce_fieldelseself._sms_get_number_fields()
        forrecordinself:
            all_numbers=[record[fname]forfnameintocheck_fieldsiffnameinrecord]
            all_partners=record._sms_get_default_partners()

            valid_number=False
            forfnamein[fforfintocheck_fieldsiffinrecord]:
                valid_number=phone_validation.phone_sanitize_numbers_w_record([record[fname]],record)[record[fname]]['sanitized']
                ifvalid_number:
                    break

            ifvalid_number:
                result[record.id]={
                    'partner':all_partners[0]ifall_partnerselseself.env['res.partner'],
                    'sanitized':valid_number,
                    'number':record[fname],
                    'partner_store':False,
                    'field_store':fname,
                }
            elifall_partnersandpartner_fallback:
                partner=self.env['res.partner']
                forpartnerinall_partners:
                    forfnameinself.env['res.partner']._sms_get_number_fields():
                        valid_number=phone_validation.phone_sanitize_numbers_w_record([partner[fname]],record)[partner[fname]]['sanitized']
                        ifvalid_number:
                            break

                ifnotvalid_number:
                    fname='mobile'ifpartner.mobileelse('phone'ifpartner.phoneelse'mobile')

                result[record.id]={
                    'partner':partner,
                    'sanitized':valid_numberifvalid_numberelseFalse,
                    'number':partner[fname],
                    'partner_store':True,
                    'field_store':fname,
                }
            else:
                #didnotfindanysanitizednumber->takefirstsetvalueasfallback;
                #ifnone,justassignFalsetothefirstavailablenumberfield
                value,fname=next(
                    ((value,fname)forvalue,fnameinzip(all_numbers,tocheck_fields)ifvalue),
                    (False,tocheck_fields[0]iftocheck_fieldselseFalse)
                )
                result[record.id]={
                    'partner':self.env['res.partner'],
                    'sanitized':False,
                    'number':value,
                    'partner_store':False,
                    'field_store':fname
                }
        returnresult

    def_message_sms_schedule_mass(self,body='',template=False,active_domain=None,**composer_values):
        """Shortcutmethodtoscheduleamasssmssendingonarecordset.

        :paramtemplate:anoptionalsms.templaterecord;
        :paramactive_domain:bypassself.idsandapplycomposeronactive_domain
          instead;
        """
        composer_context={
            'default_res_model':self._name,
            'default_composition_mode':'mass',
            'default_template_id':template.idiftemplateelseFalse,
            'default_body':bodyifbodyandnottemplateelseFalse,
        }
        ifactive_domainisnotNone:
            composer_context['default_use_active_domain']=True
            composer_context['default_active_domain']=repr(active_domain)
        else:
            composer_context['default_res_ids']=self.ids

        create_vals={
            'mass_force_send':False,
            'mass_keep_log':True,
        }
        ifcomposer_values:
            create_vals.update(composer_values)

        composer=self.env['sms.composer'].with_context(**composer_context).create(create_vals)
        returncomposer._action_send_sms()

    def_message_sms_with_template(self,template=False,template_xmlid=False,template_fallback='',partner_ids=False,**kwargs):
        """Shortcutmethodtoperforma_message_smswithansms.template.

        :paramtemplate:avalidsms.templaterecord;
        :paramtemplate_xmlid:XMLIDofansms.template(ifnotemplategiven);
        :paramtemplate_fallback:plaintext(jinja-enabled)incasetemplate
          andtemplatexmlidarefalsy(forexampleduetodeleteddata);
        """
        self.ensure_one()
        ifnottemplateandtemplate_xmlid:
            template=self.env.ref(template_xmlid,raise_if_not_found=False)
        iftemplate:
            body=template._render_field('body',self.ids,compute_lang=True)[self.id]
        else:
            body=self.env['sms.template']._render_template(template_fallback,self._name,self.ids)[self.id]
        returnself._message_sms(body,partner_ids=partner_ids,**kwargs)

    def_message_sms(self,body,subtype_id=False,partner_ids=False,number_field=False,
                     sms_numbers=None,sms_pid_to_number=None,**kwargs):
        """MainmethodtopostamessageonarecordusingSMS-basednotification
        method.

        :parambody:contentofSMS;
        :paramsubtype_id:mail.message.subtypeusedinmail.messageassociated
          tothesmsnotificationprocess;
        :parampartner_ids:ifsetisarecordsetofpartnerstonotify;
        :paramnumber_field:ifsetisanameoffieldtouseoncurrentrecord
          tocomputeanumbertonotify;
        :paramsms_numbers:see``_notify_record_by_sms``;
        :paramsms_pid_to_number:see``_notify_record_by_sms``;
        """
        self.ensure_one()
        sms_pid_to_number=sms_pid_to_numberifsms_pid_to_numberisnotNoneelse{}

        ifnumber_fieldor(partner_idsisFalseandsms_numbersisNone):
            info=self._sms_get_recipients_info(force_field=number_field)[self.id]
            info_partner_ids=info['partner'].idsifinfo['partner']elseFalse
            info_number=info['sanitized']ifinfo['sanitized']elseinfo['number']
            ifinfo_partner_idsandinfo_number:
                sms_pid_to_number[info_partner_ids[0]]=info_number
            ifinfo_partner_ids:
                partner_ids=info_partner_ids+(partner_idsor[])
            ifnotinfo_partner_ids:
                ifinfo_number:
                    sms_numbers=[info_number]+(sms_numbersor[])
                    #willsendafalsynotificationallowingtofixitthroughSMSwizards
                elifnotsms_numbers:
                    sms_numbers=[False]

        ifsubtype_idisFalse:
            subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note')

        returnself.message_post(
            body=plaintext2html(html2plaintext(body)),partner_ids=partner_idsor[], #TDEFIXME:tempfixotherwisecrashmail_thread.py
            message_type='sms',subtype_id=subtype_id,
            sms_numbers=sms_numbers,sms_pid_to_number=sms_pid_to_number,
            **kwargs
        )

    def_notify_thread(self,message,msg_vals=False,**kwargs):
        recipients_data=super(MailThread,self)._notify_thread(message,msg_vals=msg_vals,**kwargs)
        self._notify_record_by_sms(message,recipients_data,msg_vals=msg_vals,**kwargs)
        returnrecipients_data

    def_notify_record_by_sms(self,message,recipients_data,msg_vals=False,
                              sms_numbers=None,sms_pid_to_number=None,
                              check_existing=False,put_in_queue=False,**kwargs):
        """Notificationmethod:bySMS.

        :parammessage:mail.messagerecordtonotify;
        :paramrecipients_data:see``_notify_thread``;
        :parammsg_vals:see``_notify_thread``;

        :paramsms_numbers:additionalnumberstonotifyinadditiontopartners
          andclassicrecipients;
        :parampid_to_number:forceanumbertonotifyforagivenpartnerID
              insteadoftakingitsmobile/phonenumber;
        :paramcheck_existing:checkforexistingnotificationstoupdatebasedon
          mailedrecipient,otherwisecreatenewnotifications;
        :paramput_in_queue:usecrontosendqueuedSMSinsteadofsendingthem
          directly;
        """
        sms_pid_to_number=sms_pid_to_numberifsms_pid_to_numberisnotNoneelse{}
        sms_numbers=sms_numbersifsms_numbersisnotNoneelse[]
        sms_create_vals=[]
        sms_all=self.env['sms.sms'].sudo()

        #pre-computeSMSdata
        body=msg_vals['body']ifmsg_valsandmsg_vals.get('body')elsemessage.body
        sms_base_vals={
            'body':html2plaintext(body),
            'mail_message_id':message.id,
            'state':'outgoing',
        }

        #notifyfromcomputedrecipients_data(followers,specificrecipients)
        partners_data=[rforrinrecipients_data['partners']ifr['notif']=='sms']
        partner_ids=[r['id']forrinpartners_data]
        ifpartner_ids:
            forpartnerinself.env['res.partner'].sudo().browse(partner_ids):
                number=sms_pid_to_number.get(partner.id)orpartner.mobileorpartner.phone
                sanitize_res=phone_validation.phone_sanitize_numbers_w_record([number],partner)[number]
                number=sanitize_res['sanitized']ornumber
                sms_create_vals.append(dict(
                    sms_base_vals,
                    partner_id=partner.id,
                    number=number
                ))

        #notifyfromadditionalnumbers
        ifsms_numbers:
            sanitized=phone_validation.phone_sanitize_numbers_w_record(sms_numbers,self)
            tocreate_numbers=[
                value['sanitized']ororiginal
                fororiginal,valueinsanitized.items()
            ]
            sms_create_vals+=[dict(
                sms_base_vals,
                partner_id=False,
                number=n,
                state='outgoing'ifnelse'error',
                error_code=''ifnelse'sms_number_missing',
            )fornintocreate_numbers]

        #createsmsandnotification
        existing_pids,existing_numbers=[],[]
        ifsms_create_vals:
            sms_all|=self.env['sms.sms'].sudo().create(sms_create_vals)

            ifcheck_existing:
                existing=self.env['mail.notification'].sudo().search([
                    '|',('res_partner_id','in',partner_ids),
                    '&',('res_partner_id','=',False),('sms_number','in',sms_numbers),
                    ('notification_type','=','sms'),
                    ('mail_message_id','=',message.id)
                ])
                forninexisting:
                    ifn.res_partner_id.idinpartner_idsandn.mail_message_id==message:
                        existing_pids.append(n.res_partner_id.id)
                    ifnotn.res_partner_idandn.sms_numberinsms_numbersandn.mail_message_id==message:
                        existing_numbers.append(n.sms_number)

            notif_create_values=[{
                'mail_message_id':message.id,
                'res_partner_id':sms.partner_id.id,
                'sms_number':sms.number,
                'notification_type':'sms',
                'sms_id':sms.id,
                'is_read':True, #discardInboxnotification
                'notification_status':'ready'ifsms.state=='outgoing'else'exception',
                'failure_type':''ifsms.state=='outgoing'elsesms.error_code,
            }forsmsinsms_allif(sms.partner_idandsms.partner_id.idnotinexisting_pids)or(notsms.partner_idandsms.numbernotinexisting_numbers)]
            ifnotif_create_values:
                self.env['mail.notification'].sudo().create(notif_create_values)

            ifexisting_pidsorexisting_numbers:
                forsmsinsms_all:
                    notif=next((nforninexistingif
                                 (n.res_partner_id.idinexisting_pidsandn.res_partner_id.id==sms.partner_id.id)or
                                 (notn.res_partner_idandn.sms_numberinexisting_numbersandn.sms_number==sms.number)),False)
                    ifnotif:
                        notif.write({
                            'notification_type':'sms',
                            'notification_status':'ready',
                            'sms_id':sms.id,
                            'sms_number':sms.number,
                        })

        ifsms_allandnotput_in_queue:
            sms_all.filtered(lambdasms:sms.state=='outgoing').send(auto_commit=False,raise_exception=False)

        returnTrue
