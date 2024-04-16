#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64

fromflectraimportapi,models


classMailTemplate(models.Model):
    _inherit='mail.template'

    defgenerate_email(self,res_ids,fields):
        """MethodoverriddeninordertoaddanattachmentcontainingtheISR
        tothedraftmessagewhenopeningthe'sendbymail'wizardonaninvoice.
        Thisattachmentgenerationwillonlyoccurifalltherequireddataare
        presentontheinvoice.Otherwise,noISRattachmentwillbecreated,and
        themailwillonlycontaintheinvoice(asdefinedinthemothermethod).
        """
        result=super(MailTemplate,self).generate_email(res_ids,fields)
        ifself.model!='account.move':
            returnresult

        multi_mode=True
        ifisinstance(res_ids,int):
            res_ids=[res_ids]
            multi_mode=False

        ifself.model=='account.move':
            forrecordinself.env[self.model].browse(res_ids):
                inv_print_name=self._render_field('report_name',record.ids,compute_lang=True)[record.id]
                new_attachments=[]

                include_qr_report='l10n_ch.l10n_ch_qr_report'notinself.env.context.get('l10n_ch_mail_skip_report',[])
                ifinclude_qr_reportandrecord.move_type=='out_invoice'andrecord.partner_bank_id._eligible_for_qr_code('ch_qr',record.partner_id,record.currency_id):
                    #WeaddanattachmentcontainingtheQR-bill
                    qr_report_name='QR-bill-'+inv_print_name+'.pdf'
                    qr_pdf=self.env.ref('l10n_ch.l10n_ch_qr_report')._render_qweb_pdf(record.ids)[0]
                    qr_pdf=base64.b64encode(qr_pdf)
                    new_attachments.append((qr_report_name,qr_pdf))

                record_dict=multi_modeandresult[record.id]orresult
                attachments_list=record_dict.get('attachments',False)
                ifattachments_list:
                    attachments_list.extend(new_attachments)
                else:
                    record_dict['attachments']=new_attachments
        returnresult
