#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.toolsimportmute_logger
fromflectra.testsimportcommon,tagged


@tagged('mail_message')
classTestMessageFormatPortal(common.SavepointCase):

    @mute_logger('flectra.models.unlink')
    deftest_mail_message_format(self):
        """Testthespecificmessageformattingfortheportal.
        Notablytheflagthattellsifthemessageisofsubtype'note'."""

        partner=self.env['res.partner'].create({'name':'Partner'})
        message_no_subtype=self.env['mail.message'].create([{
            'model':'res.partner',
            'res_id':partner.id,
        }])
        formatted_result=message_no_subtype.portal_message_format()
        #nodefinedsubtype->shouldreturnFalse
        self.assertFalse(formatted_result[0].get('is_message_subtype_note'))

        message_comment=self.env['mail.message'].create([{
            'model':'res.partner',
            'res_id':partner.id,
            'subtype_id':self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment'),
        }])
        formatted_result=message_comment.portal_message_format()
        #subtypeisacomment->shouldreturnFalse
        self.assertFalse(formatted_result[0].get('is_message_subtype_note'))

        message_note=self.env['mail.message'].create([{
            'model':'res.partner',
            'res_id':partner.id,
            'subtype_id':self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
        }])
        formatted_result=message_note.portal_message_format()
        #subtypeisnote->shouldreturnTrue
        self.assertTrue(formatted_result[0].get('is_message_subtype_note'))
