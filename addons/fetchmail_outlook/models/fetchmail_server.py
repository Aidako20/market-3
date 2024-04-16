#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_,api,models
fromflectra.exceptionsimportUserError


classFetchmailServer(models.Model):
    """AddtheOutlookOAuthauthenticationontheincomingmailservers."""

    _name='fetchmail.server'
    _inherit=['fetchmail.server','microsoft.outlook.mixin']

    _OUTLOOK_SCOPE='https://outlook.office.com/IMAP.AccessAsUser.All'

    @api.constrains('use_microsoft_outlook_service','server_type','password','is_ssl')
    def_check_use_microsoft_outlook_service(self):
        forserverinself:
            ifnotserver.use_microsoft_outlook_service:
                continue

            ifserver.server_type!='imap':
                raiseUserError(_('Outlookmailserver%ronlysupportsIMAPservertype.')%server.name)

            ifserver.password:
                raiseUserError(_(
                    'PleaseleavethepasswordfieldemptyforOutlookmailserver%r.'
                    'TheOAuthprocessdoesnotrequireit')
                    %server.name)

            ifnotserver.is_ssl:
                raiseUserError(_('SSLisrequired.')%server.name)

    @api.onchange('use_microsoft_outlook_service')
    def_onchange_use_microsoft_outlook_service(self):
        """SetthedefaultconfigurationforaIMAPOutlookserver."""
        ifself.use_microsoft_outlook_service:
            self.server='imap.outlook.com'
            self.server_type='imap'
            self.is_ssl=True
            self.port=993
        else:
            self.microsoft_outlook_refresh_token=False
            self.microsoft_outlook_access_token=False
            self.microsoft_outlook_access_token_expiration=False

    def_imap_login(self,connection):
        """AuthenticatetheIMAPconnection.

        IfthemailserverisOutlook,weusetheOAuth2authenticationprotocol.
        """
        self.ensure_one()
        ifself.use_microsoft_outlook_service:
            auth_string=self._generate_outlook_oauth2_string(self.user)
            connection.authenticate('XOAUTH2',lambdax:auth_string)
            connection.select('INBOX')
        else:
            super()._imap_login(connection)
