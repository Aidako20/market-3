#-*-coding:utf-8-*-
importipaddress

fromflectraimport_,SUPERUSER_ID
fromflectra.httpimportrequest
fromflectra.addons.web.controllersimportmainasweb

def_admin_password_warn(uid):
    """Adminstillhas`admin`password,flashamessageviachatter.

    Usesaprivatemail.channelfromthesystem(/flectrabot)totheuser,as
    usingamoregenericmail.threadcouldsendanemailwhichisundesirable

    Usesmail.channeldirectlybecauseusingmail.threadmightsendanemailinstead.
    """
    ifrequest.params['password']!='admin':
        return
    ifipaddress.ip_address(request.httprequest.remote_addr).is_private:
        return
    env=request.env(user=SUPERUSER_ID,su=True)
    admin=env.ref('base.partner_admin')
    ifuidnotinadmin.user_ids.ids:
        return
    has_demo=bool(env['ir.module.module'].search_count([('demo','=',True)]))
    ifhas_demo:
        return

    user=request.env(user=uid)['res.users']
    MailChannel=env(context=user.context_get())['mail.channel']
    MailChannel.browse(MailChannel.channel_get([admin.id])['id'])\
        .message_post(
            body=_("Yourpasswordisthedefault(admin)!Ifthissystemisexposedtountrustedusersitisimportanttochangeitimmediatelyforsecurityreasons.Iwillkeepnaggingyouaboutit!"),
            message_type='comment',
            subtype_xmlid='mail.mt_comment'
        )

classHome(web.Home):
    def_login_redirect(self,uid,redirect=None):
        ifrequest.params.get('login_success'):
            _admin_password_warn(uid)

        returnsuper()._login_redirect(uid,redirect)
