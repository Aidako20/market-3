#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,fields,_


classAccountMove(models.Model):
    _inherit='account.move'

    edi_show_abandon_cancel_button=fields.Boolean(
        compute='_compute_edi_show_abandon_cancel_button')
    edi_error_message=fields.Html(compute='_compute_edi_error_message')
    edi_blocking_level=fields.Selection(selection=[('info','Info'),('warning','Warning'),('error','Error')],compute='_compute_edi_error_message')

    @api.depends(
        'edi_document_ids',
        'edi_document_ids.state',
        'edi_document_ids.blocking_level',
        'edi_document_ids.edi_format_id',
        'edi_document_ids.edi_format_id.name')
    def_compute_edi_web_services_to_process(self):
        #OVERRIDEtotakeblocking_levelintoaccount
        formoveinself:
            to_process=move.edi_document_ids.filtered(lambdad:d.statein['to_send','to_cancel']andd.blocking_level!='error')
            format_web_services=to_process.edi_format_id.filtered(lambdaf:f._needs_web_services())
            move.edi_web_services_to_process=','.join(f.nameforfinformat_web_services)

    @api.depends(
        'state',
        'edi_document_ids.state',
        'edi_document_ids.attachment_id')
    def_compute_edi_show_abandon_cancel_button(self):
        formoveinself:
            move.edi_show_abandon_cancel_button=any(doc.edi_format_id._needs_web_services()
                                                      anddoc.state=='to_cancel'
                                                      andmove.is_invoice(include_receipts=True)
                                                      anddoc.edi_format_id._is_required_for_invoice(move)
                                                      fordocinmove.edi_document_ids)

    @api.depends('edi_error_count','edi_document_ids.error','edi_document_ids.blocking_level')
    def_compute_edi_error_message(self):
        formoveinself:
            ifmove.edi_error_count==0:
                move.edi_error_message=None
                move.edi_blocking_level=None
            elifmove.edi_error_count==1:
                error_doc=move.edi_document_ids.filtered(lambdad:d.error)
                move.edi_error_message=error_doc.error
                move.edi_blocking_level=error_doc.blocking_level
            else:
                error_levels=set([doc.blocking_levelfordocinmove.edi_document_ids])
                if'error'inerror_levels:
                    move.edi_error_message=str(move.edi_error_count)+_("Electronicinvoicingerror(s)")
                    move.edi_blocking_level='error'
                elif'warning'inerror_levels:
                    move.edi_error_message=str(move.edi_error_count)+_("Electronicinvoicingwarning(s)")
                    move.edi_blocking_level='warning'
                else:
                    move.edi_error_message=str(move.edi_error_count)+_("Electronicinvoicinginfo(s)")
                    move.edi_blocking_level='info'

    defaction_retry_edi_documents_error(self):
        self.edi_document_ids.write({'error':False,'blocking_level':False})
        self.action_process_edi_web_services()

    defbutton_abandon_cancel_posted_posted_moves(self):
        '''CanceltherequestforcancellationoftheEDI.
        '''
        documents=self.env['account.edi.document']
        formoveinself:
            is_move_marked=False
            fordocinmove.edi_document_ids:
                ifdoc.state=='to_cancel'\
                        andmove.is_invoice(include_receipts=True)\
                        anddoc.edi_format_id._is_required_for_invoice(move):
                    documents|=doc
                    is_move_marked=True
            ifis_move_marked:
                move.message_post(body=_("ArequestforcancellationoftheEDIhasbeencalledoff."))

        documents.write({'state':'sent'})
