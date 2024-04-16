
fromflectraimportapi,fields,models

classSnailmailLetterFormatError(models.TransientModel):
    _name='snailmail.letter.format.error'
    _description='FormatErrorSendingaSnailmailLetter'

    message_id=fields.Many2one(
        'mail.message',
        default=lambdaself:self.env.context.get('message_id',None),
    )
    snailmail_cover=fields.Boolean(
        string='AddaCoverPage',
        default=lambdaself:self.env.company.snailmail_cover,
    )

    defupdate_resend_action(self):
        self.env.company.write({'snailmail_cover':self.snailmail_cover})
        letters_to_resend=self.env['snailmail.letter'].search([
            ('error_code','=','FORMAT_ERROR'),
        ])
        forletterinletters_to_resend:
            old_attachment=letter.attachment_id
            letter.attachment_id=False
            old_attachment.unlink()
            letter.write({'cover':self.snailmail_cover})
            letter.snailmail_print()

    defcancel_letter_action(self):
        self.message_id.cancel_letter()
