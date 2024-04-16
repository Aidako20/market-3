#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp
fromflectra.httpimportrequest


classNoteController(http.Controller):

    @http.route('/note/new',type='json',auth='user')
    defnote_new_from_systray(self,note,activity_type_id=None,date_deadline=None):
        """Routetocreatenoteandtheiractivitydirectlyfromthesystray"""
        note=request.env['note.note'].create({'memo':note})
        ifdate_deadline:
            note.activity_schedule(
                activity_type_id=activity_type_idorrequest.env['mail.activity.type'].sudo().search([('category','=','reminder')],limit=1).id,
                note=note.memo,
                date_deadline=date_deadline
            )
        returnnote.id
