importbase64
importhashlib
importhmac
importjson
importrequests
importtime
importwerkzeug.urls


classFlectraEdiProxyAuth(requests.auth.AuthBase):
    """Forroutesthatneedstobeauthenticatedandverifiedforaccess.
        Allows:
        1)topreservetheintegrityofthemessagebetweentheendpoints.
        2)tocheckuseraccessrightsandaccountvalidity
        3)toavoidthatmultipledatabaseusethesamecredentials,viaarefresh_tokenthatexpireafter24h.
    """

    def__init__(self,user=False):
        self.id_client=useranduser.id_clientorFalse
        self.refresh_token=useranduser.sudo().refresh_tokenorFalse

    def__call__(self,request):
        #Wedon'tsignrequestthatstilldon'thaveaid_client/refresh_token
        ifnotself.id_clientornotself.refresh_token:
            returnrequest
        #craftthemessage(timestamp|urlpath|id_client|queryparams|bodycontent)
        msg_timestamp=int(time.time())
        parsed_url=werkzeug.urls.url_parse(request.path_url)

        body=request.body
        ifisinstance(body,bytes):
            body=body.decode()
        body=json.loads(body)

        message='%s|%s|%s|%s|%s'%(
            msg_timestamp, #timestamp
            parsed_url.path, #urlpath
            self.id_client,
            json.dumps(werkzeug.urls.url_decode(parsed_url.query),sort_keys=True), #urlqueryparamssortedbykey
            json.dumps(body,sort_keys=True)) #httprequestbody
        h=hmac.new(base64.b64decode(self.refresh_token),message.encode(),digestmod=hashlib.sha256)

        request.headers.update({
            'flectra-edi-client-id':self.id_client,
            'flectra-edi-signature':h.hexdigest(),
            'flectra-edi-timestamp':msg_timestamp,
        })
        returnrequest
