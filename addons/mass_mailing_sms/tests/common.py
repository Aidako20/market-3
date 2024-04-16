#-*-coding:utf-8-*-

importre
importwerkzeug

fromflectraimporttools
fromflectra.addons.mass_mailing.tests.commonimportMassMailCommon
fromflectra.addons.sms.tests.commonimportSMSCase,SMSCommon


classMassSMSCase(SMSCase):

    #------------------------------------------------------------
    #ASSERTS
    #------------------------------------------------------------

    defassertSMSStatistics(self,recipients_info,mailing,records,check_sms=True):
        """Deprecated,removein14.4"""
        returnself.assertSMSTraces(recipients_info,mailing,records,check_sms=check_sms)

    defassertSMSTraces(self,recipients_info,mailing,records,
                        check_sms=True,sent_unlink=False,
                        sms_links_info=None):
        """Checkcontentoftraces.Tracesarefetchedbasedonagivenmailing
        andrecords.Theircontentiscomparedtorecipients_infostructurethat
        holdsexpectedinformation.Linkscontentmaybechecked,notablyto
        assertshorteningorunsubscribelinks.Sms.smsrecordsmayoptionally
        bechecked.

        :paramrecipients_info:list[{
          #TRACE
          'partner':res.partnerrecord(maybeempty),
          'number':numberusedfornotification(maybeempty,computedbasedonpartner),
          'state':outgoing/sent/ignored/bounced/exception/opened(outgoingbydefault),
          'record:linkedrecord,
          #SMS.SMS
          'content':optional:ifset,checkcontentofsentSMS;
          'failure_type':errorcodelinkedtosmsfailure(see``error_code``
            fieldon``sms.sms``model);
          },
          {...}];
        :parammailing:amailing.mailingrecordfromwhichtraceshavebeen
          generated;
        :paramrecords:recordsgiventomailingthatgeneratedtraces.Itis
          usednotablytofindtracesusingtheirIDs;
        :paramcheck_sms:ifset,checksms.smsrecordsthatshouldbelinkedtotraces;
        :paramsent_unlink:itTrue,sentsms.smsaredeletedandwecheckgateway
          outputresultinsteadofactualsms.smsrecords;
        :paramsms_links_info:ifgiven,shouldfolloworderof``recipients_info``
          andgivedetailsaboutlinks.See``assertLinkShortenedHtml``helperfor
          moredetailsaboutcontenttogive;
        ]
        """
        #maptracestatetosmsstate
        state_mapping={
            'sent':'sent',
            'outgoing':'outgoing',
            'exception':'error',
            'ignored':'canceled',
            'bounced':'error',
        }
        traces=self.env['mailing.trace'].search([
            ('mass_mailing_id','in',mailing.ids),
            ('res_id','in',records.ids)
        ])

        self.assertTrue(all(s.model==records._nameforsintraces))
        #self.assertTrue(all(s.utm_campaign_id==mailing.campaign_idforsintraces))
        self.assertEqual(set(s.res_idforsintraces),set(records.ids))

        #checkeachtrace
        ifnotsms_links_info:
            sms_links_info=[None]*len(recipients_info)
        forrecipient_info,link_info,recordinzip(recipients_info,sms_links_info,records):
            partner=recipient_info.get('partner',self.env['res.partner'])
            number=recipient_info.get('number')
            state=recipient_info.get('state','outgoing')
            content=recipient_info.get('content',None)
            ifnumberisNoneandpartner:
                number=partner._sms_get_recipients_info()[partner.id]['sanitized']

            trace=traces.filtered(
                lambdat:t.sms_number==numberandt.state==stateand(t.res_id==record.idifrecordelseTrue)
            )
            self.assertTrue(len(trace)==1,
                            'SMS:found%snotificationfornumber%s,(state:%s)(1expected)'%(len(trace),number,state))
            self.assertTrue(bool(trace.sms_sms_id_int))

            ifcheck_sms:
                ifstate=='sent':
                    ifsent_unlink:
                        self.assertSMSIapSent([number],content=content)
                    else:
                        self.assertSMS(partner,number,'sent',content=content)
                elifstateinstate_mapping:
                    sms_state=state_mapping[state]
                    error_code=recipient_info['failure_type']ifstatein('exception','ignored','bounced')elseNone
                    self.assertSMS(partner,number,sms_state,error_code=error_code,content=content)
                else:
                    raiseNotImplementedError()

            iflink_info:
                #shortenedlinksaredirectlyincludedinsms.smsrecordaswellas
                #insentsms(notlikemailswhoarepost-processed)
                sms_sent=self._find_sms_sent(partner,number)
                sms_sms=self._find_sms_sms(partner,number,state_mapping[state])
                for(url,is_shortened,add_link_params)inlink_info:
                    ifurl=='unsubscribe':
                        url='%s/sms/%d/%s'%(mailing.get_base_url(),mailing.id,trace.sms_code)
                    link_params={'utm_medium':'SMS','utm_source':mailing.name}
                    ifadd_link_params:
                        link_params.update(**add_link_params)
                    self.assertLinkShortenedText(
                        sms_sms.body,
                        (url,is_shortened),
                        link_params=link_params,
                    )
                    self.assertLinkShortenedText(
                        sms_sent['body'],
                        (url,is_shortened),
                        link_params=link_params,
                    )

    #------------------------------------------------------------
    #GATEWAYTOOLS
    #------------------------------------------------------------

    defgateway_sms_click(self,mailing,record):
        """SimulateaclickonasentSMS.Usage:givingapartnerand/or
        anumber,findanSMSsenttohim,findshortenedlinksinitsbody
        andcalladd_clicktosimulateaclick."""
        trace=mailing.mailing_trace_ids.filtered(lambdat:t.model==record._nameandt.res_id==record.id)
        sms_sent=self._find_sms_sent(self.env['res.partner'],trace.sms_number)
        self.assertTrue(bool(sms_sent))
        returnself.gateway_sms_sent_click(sms_sent)

    defgateway_sms_sent_click(self,sms_sent):
        """WhenclickingonalinkinaSMSweactuallydon'thaveany
        easyinformationinbody,onlybody.Wecurrentlyclickonallfound
        shortenedlinks."""
        forurlinre.findall(tools.TEXT_URL_REGEX,sms_sent['body']):
            if'/r/'inurl: #shortenedlink,like'http://localhost:7073/r/LBG/s/53'
                parsed_url=werkzeug.urls.url_parse(url)
                path_items=parsed_url.path.split('/')
                code,sms_sms_id=path_items[2],int(path_items[4])
                trace_id=self.env['mailing.trace'].sudo().search([('sms_sms_id_int','=',sms_sms_id)]).id

                self.env['link.tracker.click'].sudo().add_click(
                    code,
                    ip='100.200.300.400',
                    country_code='BE',
                    mailing_trace_id=trace_id
                )


classMassSMSCommon(MassMailCommon,SMSCommon,MassSMSCase):

    @classmethod
    defsetUpClass(cls):
        super(MassSMSCommon,cls).setUpClass()
