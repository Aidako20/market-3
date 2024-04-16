#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api,_
fromflectra.addons.account_edi_extended.models.account_edi_documentimportDEFAULT_BLOCKING_LEVEL
fromflectra.exceptionsimportUserError

frompsycopg2importOperationalError
importbase64
importlogging

_logger=logging.getLogger(__name__)


classAccountEdiDocument(models.Model):
    _name='account.edi.document'
    _description='ElectronicDocumentforanaccount.move'

    #==Storedfields==
    move_id=fields.Many2one('account.move',required=True,ondelete='cascade')
    edi_format_id=fields.Many2one('account.edi.format',required=True)
    attachment_id=fields.Many2one('ir.attachment',help='Thefilegeneratedbyedi_format_idwhentheinvoiceisposted(andthisdocumentisprocessed).')
    state=fields.Selection([('to_send','ToSend'),('sent','Sent'),('to_cancel','ToCancel'),('cancelled','Cancelled')])
    error=fields.Html(help='ThetextofthelasterrorthathappenedduringElectronicInvoiceoperation.')

    #==Notstoredfields==
    name=fields.Char(related='attachment_id.name')
    edi_format_name=fields.Char(string='FormatName',related='edi_format_id.name')
    edi_content=fields.Binary(compute='_compute_edi_content',compute_sudo=True)

    _sql_constraints=[
        (
            'unique_edi_document_by_move_by_format',
            'UNIQUE(edi_format_id,move_id)',
            'Onlyoneedidocumentbymovebyformat',
        ),
    ]

    @api.depends('move_id','error','state')
    def_compute_edi_content(self):
        fordocinself:
            res=b''
            ifdoc.statein('to_send','to_cancel'):
                move=doc.move_id
                config_errors=doc.edi_format_id._check_move_configuration(move)
                ifconfig_errors:
                    res=base64.b64encode('\n'.join(config_errors).encode('UTF-8'))
                elifmove.is_invoice(include_receipts=True)anddoc.edi_format_id._is_required_for_invoice(move):
                    res=base64.b64encode(doc.edi_format_id._get_invoice_edi_content(doc.move_id))
                elifmove.payment_idanddoc.edi_format_id._is_required_for_payment(move):
                    res=base64.b64encode(doc.edi_format_id._get_payment_edi_content(doc.move_id))
            doc.edi_content=res

    defaction_export_xml(self):
        self.ensure_one()
        return{
            'type':'ir.actions.act_url',
            'url': '/web/content/account.edi.document/%s/edi_content'%self.id
        }

    defwrite(self,vals):
        '''Ifaccount_edi_extendedisnotinstalled,adefaultbehaviourisusedinstead.
        '''
        if'blocking_level'invalsand'blocking_level'notinself.env['account.edi.document']._fields:
            vals.pop('blocking_level')

        returnsuper().write(vals)

    def_prepare_jobs(self):
        """Createsalistofjobstobeperformedby'_process_job'forthedocumentsinself.
        Eachdocumentrepresentajob,BUTifmultipledocumentshavethesamestate,edi_format_id,
        doc_type(invoiceorpayment)andcompany_idANDtheedi_format_idsupportsbatching,theyaregrouped
        intoasinglejob.

        :returns:        Alistoftuples(documents,doc_type)
        *documents:     Thedocumentsrelatedtothisjob.Ifedi_format_iddoesnotsupportbatch,lengthisone
        *doc_type:      Arethemovesofthisjobinvoiceorpayments?
        """

        #Classifyjobsby(edi_format,edi_doc.state,doc_type,move.company_id,custom_key)
        to_process={}
        if'blocking_level'inself.env['account.edi.document']._fields:
            documents=self.filtered(lambdad:d.statein('to_send','to_cancel')andd.blocking_level!='error')
        else:
            documents=self.filtered(lambdad:d.statein('to_send','to_cancel'))
        foredi_docindocuments:
            move=edi_doc.move_id
            edi_format=edi_doc.edi_format_id
            ifmove.is_invoice(include_receipts=True):
                doc_type='invoice'
            elifmove.payment_idormove.statement_line_id:
                doc_type='payment'
            else:
                continue

            custom_key=edi_format._get_batch_key(edi_doc.move_id,edi_doc.state)
            key=(edi_format,edi_doc.state,doc_type,move.company_id,custom_key)
            to_process.setdefault(key,self.env['account.edi.document'])
            to_process[key]|=edi_doc

        #Orderpayments/invoiceandcreatebatches.
        invoices=[]
        payments=[]
        forkey,documentsinto_process.items():
            edi_format,state,doc_type,company_id,custom_key=key
            target=invoicesifdoc_type=='invoice'elsepayments
            batch=self.env['account.edi.document']
            fordocindocuments:
                ifedi_format._support_batching(move=doc.move_id,state=state,company=company_id):
                    batch|=doc
                else:
                    target.append((doc,doc_type))
            ifbatch:
                target.append((batch,doc_type))
        returninvoices+payments

    @api.model
    def_convert_to_old_jobs_format(self,jobs):
        """See'_prepare_jobs':
        Oldformat:((edi_format,state,doc_type,company_id),documents)
        Sinceedi_format,stateandcompany_idcanbededucedfromdocuments,thisisredundantandmorepronetounexpectedbehaviours.
        Newformat:(doc_type,documents).

        However,forbackwardcompatibilityof'process_jobs',weneedawaytoconvertbacktotheoldformat.
        """
        return[(
            (documents.edi_format_id,documents[0].state,doc_type,documents.move_id.company_id),
            documents
        )fordocuments,doc_typeinjobs]

    @api.model
    def_process_jobs(self,to_process):
        """Deprecated,use_process_jobinstead.

        :paramto_process:Alistoftuples(key,documents)
        *key:            Atuple(edi_format_id,state,doc_type,company_id)
        **edi_format_id: Theformattoperformtheoperationwith
        **state:         Thestateofthedocumentsofthisjob
        **doc_type:      Arethemovesofthisjobinvoiceorpayments?
        **company_id:    Thecompanythemovesbelongto
        *documents:      Thedocumentsrelatedtothisjob.Ifedi_format_iddoesnotsupportbatch,lengthisone
        """
        forkey,documentsinto_process:
            edi_format,state,doc_type,company_id=key
            self._process_job(documents,doc_type)

    @api.model
    def_process_job(self,documents,doc_type):
        """Postorcancelmove_id(invoiceorpayment)bycallingtherelatedmethodsonedi_format_id.
        Invoicesareprocessedbeforepayments.

        :paramdocuments:Thedocumentsrelatedtothisjob.Ifedi_format_iddoesnotsupportbatch,lengthisone
        :paramdoc_type: Arethemovesofthisjobinvoiceorpayments?
        """
        def_postprocess_post_edi_results(documents,edi_result):
            attachments_to_unlink=self.env['ir.attachment']
            fordocumentindocuments:
                move=document.move_id
                move_result=edi_result.get(move,{})
                ifmove_result.get('attachment'):
                    old_attachment=document.attachment_id
                    values={
                        'attachment_id':move_result['attachment'].id,
                        'error':move_result.get('error',False),
                        'blocking_level':move_result.get('blocking_level',DEFAULT_BLOCKING_LEVEL)if'error'inmove_resultelseFalse,
                    }
                    ifnotvalues.get('error'):
                        values.update({'state':'sent'})
                    document.write(values)
                    ifnotold_attachment.res_modelornotold_attachment.res_id:
                        attachments_to_unlink|=old_attachment
                else:
                    document.write({
                        'error':move_result.get('error',False),
                        'blocking_level':move_result.get('blocking_level',DEFAULT_BLOCKING_LEVEL)if'error'inmove_resultelseFalse,
                    })

            #Attachmentsthatarenotexplicitlylinkedtoabusinessmodelcouldberemovedbecausetheyarenot
            #supposedtohaveanytraceabilityfromtheuser.
            attachments_to_unlink.unlink()

        def_postprocess_cancel_edi_results(documents,edi_result):
            invoice_ids_to_cancel=set() #Avoidduplicates
            attachments_to_unlink=self.env['ir.attachment']
            fordocumentindocuments:
                move=document.move_id
                move_result=edi_result.get(move,{})
                ifmove_result.get('success')isTrue:
                    old_attachment=document.sudo().attachment_id
                    document.write({
                        'state':'cancelled',
                        'error':False,
                        'attachment_id':False,
                        'blocking_level':False,
                    })

                    ifmove.is_invoice(include_receipts=True)andmove.state=='posted':
                        #TheuserrequestedacancellationoftheEDIandithasbeenapproved.Then,theinvoice
                        #canbesafelycancelled.
                        invoice_ids_to_cancel.add(move.id)

                    ifnotold_attachment.res_modelornotold_attachment.res_id:
                        attachments_to_unlink|=old_attachment

                elifnotmove_result.get('success'):
                    document.write({
                        'error':move_result.get('error',False),
                        'blocking_level':move_result.get('blocking_level',DEFAULT_BLOCKING_LEVEL)ifmove_result.get('error')elseFalse,
                    })

            ifinvoice_ids_to_cancel:
                invoices=self.env['account.move'].browse(list(invoice_ids_to_cancel))
                invoices.button_draft()
                invoices.button_cancel()

            #Attachmentsthatarenotexplicitlylinkedtoabusinessmodelcouldberemovedbecausetheyarenot
            #supposedtohaveanytraceabilityfromtheuser.
            attachments_to_unlink.sudo().unlink()

        test_mode=self._context.get('edi_test_mode',False)

        documents.edi_format_id.ensure_one() #Allaccount.edi.documentofajobshouldhavethesameedi_format_id
        documents.move_id.company_id.ensure_one() #Allaccount.edi.documentofajobshouldbefromthesamecompany
        iflen(set(doc.statefordocindocuments))!=1:
            raiseValueError('Allaccount.edi.documentofajobshouldhavethesamestate')

        edi_format=documents.edi_format_id
        state=documents[0].state
        ifdoc_type=='invoice':
            ifstate=='to_send':
                edi_result=edi_format._post_invoice_edi(documents.move_id,test_mode=test_mode)
                _postprocess_post_edi_results(documents,edi_result)
            elifstate=='to_cancel':
                edi_result=edi_format._cancel_invoice_edi(documents.move_id,test_mode=test_mode)
                _postprocess_cancel_edi_results(documents,edi_result)

        elifdoc_type=='payment':
            ifstate=='to_send':
                edi_result=edi_format._post_payment_edi(documents.move_id,test_mode=test_mode)
                _postprocess_post_edi_results(documents,edi_result)
            elifstate=='to_cancel':
                edi_result=edi_format._cancel_payment_edi(documents.move_id,test_mode=test_mode)
                _postprocess_cancel_edi_results(documents,edi_result)

    def_process_documents_no_web_services(self):
        """Postandcancelallthedocumentsthatdon'tneedawebservice.
        """
        jobs=self.filtered(lambdad:notd.edi_format_id._needs_web_services())._prepare_jobs()
        self._process_jobs(self._convert_to_old_jobs_format(jobs))

    def_process_documents_web_services(self,job_count=None,with_commit=True):
        """Postandcancelallthedocumentsthatneedawebservice.ThisiscalledbyCRON.

        :paramjob_count:Limittothenumberofjobstoprocessamongtheonesthatareavailablefortreatment.
        """
        jobs=self.filtered(lambdad:d.edi_format_id._needs_web_services())._prepare_jobs()
        jobs=jobs[0:job_countorlen(jobs)]
        fordocuments,doc_typeinjobs:
            move_to_lock=documents.move_id
            attachments_potential_unlink=documents.attachment_id.filtered(lambdaa:nota.res_modelandnota.res_id)
            try:
                withself.env.cr.savepoint():
                    self._cr.execute('SELECT*FROMaccount_edi_documentWHEREidIN%sFORUPDATENOWAIT',[tuple(documents.ids)])
                    self._cr.execute('SELECT*FROMaccount_moveWHEREidIN%sFORUPDATENOWAIT',[tuple(move_to_lock.ids)])

                    #Lockstheattachmentsthatmightbeunlinked
                    ifattachments_potential_unlink:
                        self._cr.execute('SELECT*FROMir_attachmentWHEREidIN%sFORUPDATENOWAIT',[tuple(attachments_potential_unlink.ids)])

            exceptOperationalErrorase:
                ife.pgcode=='55P03':
                    _logger.debug('Anothertransactionalreadylockeddocumentsrows.Cannotprocessdocuments.')
                    ifnotwith_commit:
                        raiseUserError(_('Thisdocumentisbeingsentbyanotherprocessalready.'))
                    continue
                else:
                    raisee

            self._process_job(documents,doc_type)
            ifwith_commitandlen(jobs)>1:
                self.env.cr.commit()
