#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels

classMailThread(models.AbstractModel):
    _inherit='mail.thread'

    def_message_post_process_attachments(self,attachments,attachment_ids,message_values):
        """Thismethodextensionensuresthat,whenusingthe"Send&Print"feature,iftheuser
        addsanattachment,thelatterwillbelinkedtotherecord."""
        record=self.env.context.get('attached_to')
        #linkmail.compose.messageattachmentstoattached_to
        ifrecordandrecord._name=='account.move':
            message_values['model']=record._name
            message_values['res_id']=record.id
        res=super()._message_post_process_attachments(attachments,attachment_ids,message_values)
        #linkaccount.invoice.sendattachmentstoattached_to
        model=message_values['model']
        res_id=message_values['res_id']
        att_ids=[att[1]forattinres.get('attachment_ids')or[]]
        ifatt_idsandmodel=='account.move':
            filtered_attachment_ids=self.env['ir.attachment'].sudo().browse(att_ids).filtered(
                lambdaa:a.res_modelin('account.invoice.send',)anda.create_uid.id==self._uid)
            iffiltered_attachment_ids:
                filtered_attachment_ids.write({'res_model':model,'res_id':res_id})
        returnres
