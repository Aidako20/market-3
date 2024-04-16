#-*-coding:utf-8-*-

fromflectraimportapi,models,SUPERUSER_ID


classAccountMove(models.Model):
    _inherit='account.move'

    definvoice_validate_send_email(self):
        ifself.env.su:
            #sendingmailinsudowasmeantforitbeingsentfromsuperuser
            self=self.with_user(SUPERUSER_ID)
        forinvoiceinself.filtered(lambdax:x.move_type=='out_invoice'):
            #sendtemplateonlyoncustomerinvoice
            #subscribethepartnertotheinvoice
            ifinvoice.partner_idnotininvoice.message_partner_ids:
                invoice.message_subscribe([invoice.partner_id.id])
            forlineininvoice.invoice_line_ids:
                ifline.product_id.email_template_id:
                    invoice.message_post_with_template(
                        line.product_id.email_template_id.id,
                        composition_mode="comment",
                        email_layout_xmlid="mail.mail_notification_light"
                    )
        returnTrue

    def_post(self,soft=True):
        #OVERRIDE
        posted=super()._post(soft)
        posted.invoice_validate_send_email()
        returnposted
