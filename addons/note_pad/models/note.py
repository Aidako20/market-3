#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classNotePad(models.Model):

    _name='note.note'
    _inherit=['pad.common','note.note']

    _pad_fields=['note_pad']

    note_pad_url=fields.Char('PadUrl',pad_content_field='memo',copy=False)
