#-*-coding:utf-8-*-

fromflectraimportapi,fields,models
fromflectra.addons.bus.models.bus_presenceimportAWAY_TIMER
fromflectra.addons.bus.models.bus_presenceimportDISCONNECTION_TIMER


classResUsers(models.Model):

    _inherit="res.users"

    im_status=fields.Char('IMStatus',compute='_compute_im_status')

    def_compute_im_status(self):
        """Computetheim_statusoftheusers"""
        self.env.cr.execute("""
            SELECT
                user_idasid,
                CASEWHENage(now()ATTIMEZONE'UTC',last_poll)>interval%sTHEN'offline'
                     WHENage(now()ATTIMEZONE'UTC',last_presence)>interval%sTHEN'away'
                     ELSE'online'
                ENDasstatus
            FROMbus_presence
            WHEREuser_idIN%s
        """,("%sseconds"%DISCONNECTION_TIMER,"%sseconds"%AWAY_TIMER,tuple(self.ids)))
        res=dict(((status['id'],status['status'])forstatusinself.env.cr.dictfetchall()))
        foruserinself:
            user.im_status=res.get(user.id,'offline')
