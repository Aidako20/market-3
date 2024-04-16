#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromwerkzeug.exceptionsimportNotFound

fromflectraimporthttp
fromflectra.httpimportrequest


classWebsiteJitsiController(http.Controller):

    @http.route(["/jitsi/update_status"],type="json",auth="public")
    defjitsi_update_status(self,room_name,participant_count,joined):
        """Updateroomstatus:participantcount,maxreached

        UsetheSQLkeywords"FORUPDATESKIPLOCKED"inordertoskipiftherow
        islocked(insteadofraisinganexception,waitforamomentandretry).
        Thisendpointmaybecalledmultipletimesandwedon'tcarehavingsmall
        errorsinparticipantcountcomparedtoperformanceissues.

        :raiseValueError:wrongparticipantcount
        :raiseNotFound:wrongroomname
        """
        ifparticipant_count<0:
            raiseValueError()

        chat_room=self._chat_room_exists(room_name)
        ifnotchat_room:
            raiseNotFound()

        request.env.cr.execute(
            """
            WITHreqAS(
                SELECTid
                  FROMchat_room
                  --Cannotupdatethechatroomifwedonothaveitsname
                 WHEREname=%s
                   FORUPDATESKIPLOCKED
            )
            UPDATEchat_roomASwcr
               SETparticipant_count=%s,
                   last_activity=NOW(),
                   max_participant_reached=GREATEST(max_participant_reached,%s)
              FROMreq
             WHEREwcr.id=req.id;
            """,
            [room_name,participant_count,participant_count]
        )

    @http.route(["/jitsi/is_full"],type="json",auth="public")
    defjitsi_is_full(self,room_name):
        returnself._chat_room_exists(room_name).is_full

    #------------------------------------------------------------
    #TOOLS
    #------------------------------------------------------------

    def_chat_room_exists(self,room_name):
        returnrequest.env["chat.room"].sudo().search([("name","=",room_name)],limit=1)
