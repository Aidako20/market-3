#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classAuthOAuthProvider(models.Model):
    """ClassdefiningtheconfigurationvaluesofanOAuth2provider"""

    _name='auth.oauth.provider'
    _description='OAuth2provider'
    _order='sequence,name'

    name=fields.Char(string='Providername',required=True) #NameoftheOAuth2entity,Google,etc
    client_id=fields.Char(string='ClientID') #Ouridentifier
    auth_endpoint=fields.Char(string='AuthorizationURL',required=True) #OAuthproviderURLtoauthenticateusers
    scope=fields.Char(default='openidprofileemail') #OAUthuserdatadesiredtoaccess
    validation_endpoint=fields.Char(string='UserInfoURL',required=True) #OAuthproviderURLtogetuserinformation
    data_endpoint=fields.Char()
    enabled=fields.Boolean(string='Allowed')
    css_class=fields.Char(string='CSSclass',default='fafa-fwfa-sign-intext-primary')
    body=fields.Char(required=True,string="Loginbuttonlabel",help='LinktextinLoginDialog',translate=True)
    sequence=fields.Integer(default=10)
