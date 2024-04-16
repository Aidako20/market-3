#-*-coding:utf-8-*-

fromflectraimportapi,fields,models
fromflectra.addons.bus.models.bus_presenceimportAWAY_TIMER
fromflectra.addons.bus.models.bus_presenceimportDISCONNECTION_TIMER


classResPartner(models.Model):
    _inherit='res.partner'

    im_status=fields.Char('IMStatus',compute='_compute_im_status')

    def_compute_im_status(self):
        self.env.cr.execute("""
            SELECT
                U.partner_idasid,
                CASEWHENmax(B.last_poll)ISNULLTHEN'offline'
                    WHENage(now()ATTIMEZONE'UTC',max(B.last_poll))>interval%sTHEN'offline'
                    WHENage(now()ATTIMEZONE'UTC',max(B.last_presence))>interval%sTHEN'away'
                    ELSE'online'
                ENDasstatus
            FROMbus_presenceB
            RIGHTJOINres_usersUONB.user_id=U.id
            WHEREU.partner_idIN%sANDU.active='t'
         GROUPBYU.partner_id
        """,("%sseconds"%DISCONNECTION_TIMER,"%sseconds"%AWAY_TIMER,tuple(self.ids)))
        res=dict(((status['id'],status['status'])forstatusinself.env.cr.dictfetchall()))
        forpartnerinself:
            partner.im_status=res.get(partner.id,'im_partner') #ifnotfound,itisapartner,usefultoavoidtorefreshstatusinjs
