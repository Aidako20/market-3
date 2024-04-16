#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64

fromflectraimport_,api,models
fromflectra.exceptionsimportUserError


classIrMailServer(models.Model):
    """AddtheOutlookOAuthauthenticationontheoutgoingmailservers."""

    _name='ir.mail_server'
    _inherit=['ir.mail_server','microsoft.outlook.mixin']

    _OUTLOOK_SCOPE='https://outlook.office.com/SMTP.Send'

    @api.constrains('use_microsoft_outlook_service','smtp_pass','smtp_encryption')
    def_check_use_microsoft_outlook_service(self):
        forserverinself:
            ifnotserver.use_microsoft_outlook_service:
                continue

            ifserver.smtp_pass:
                raiseUserError(_(
                    'PleaseleavethepasswordfieldemptyforOutlookmailserver%r.'
                    'TheOAuthprocessdoesnotrequireit')
                    %server.name)

            ifserver.smtp_encryption!='starttls':
                raiseUserError(_(
                    'IncorrectConnectionSecurityforOutlookmailserver%r.'
                    'Pleasesetitto"TLS(STARTTLS)".')
                    %server.name)

            ifnotserver.smtp_user:
                raiseUserError(_(
                            'Pleasefillthe"Username"fieldwithyourOutlook/Office365username(youremailaddress).'
                            'ThisshouldbethesameaccountastheoneusedfortheOutlookOAuthenticationToken.'))

    @api.onchange('smtp_encryption')
    def_onchange_encryption(self):
        """DonotchangetheSMTPconfigurationifit'saOutlookserver

        (e.g.theportwhichisalreadyset)"""
        ifnotself.use_microsoft_outlook_service:
            super()._onchange_encryption()

    @api.onchange('use_microsoft_outlook_service')
    def_onchange_use_microsoft_outlook_service(self):
        ifself.use_microsoft_outlook_service:
            self.smtp_host='smtp.outlook.com'
            self.smtp_encryption='starttls'
            self.smtp_port=587
        else:
            self.microsoft_outlook_refresh_token=False
            self.microsoft_outlook_access_token=False
            self.microsoft_outlook_access_token_expiration=False

    def_smtp_login(self,connection,smtp_user,smtp_password):
        iflen(self)==1andself.use_microsoft_outlook_service:
            auth_string=self._generate_outlook_oauth2_string(smtp_user)
            oauth_param=base64.b64encode(auth_string.encode()).decode()
            connection.ehlo()
            connection.docmd('AUTH','XOAUTH2%s'%oauth_param)
        else:
            super()._smtp_login(connection,smtp_user,smtp_password)
