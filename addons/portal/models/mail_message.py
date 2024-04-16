#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classMailMessage(models.Model):
    _inherit='mail.message'

    defportal_message_format(self):
        returnself._portal_message_format([
            'id','body','date','author_id','email_from', #basemessagefields
            'message_type','subtype_id','is_internal','subject', #messagespecific
            'model','res_id','record_name', #documentrelated
        ])

    def_portal_message_format(self,fields_list):
        vals_list=self._message_format(fields_list)
        message_subtype_note_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note')
        IrAttachmentSudo=self.env['ir.attachment'].sudo()
        forvalsinvals_list:
            vals['is_message_subtype_note']=message_subtype_note_idand(vals.get('subtype_id')or[False])[0]==message_subtype_note_id
            forattachmentinvals.get('attachment_ids',[]):
                ifnotattachment.get('access_token'):
                    attachment['access_token']=IrAttachmentSudo.browse(attachment['id']).generate_access_token()[0]
        returnvals_list
