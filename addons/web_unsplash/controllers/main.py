#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importbase64
importlogging
importmimetypes
importrequests
importwerkzeug.utils

fromflectraimporthttp,tools,_
fromflectra.httpimportrequest
fromflectra.tools.mimetypesimportguess_mimetype
fromwerkzeug.urlsimporturl_encode

logger=logging.getLogger(__name__)


classWeb_Unsplash(http.Controller):

    def_get_access_key(self):
        ifrequest.env.user._has_unsplash_key_rights(mode='read'):
            returnrequest.env['ir.config_parameter'].sudo().get_param('unsplash.access_key')
        raisewerkzeug.exceptions.NotFound()

    def_notify_download(self,url):
        '''NotifiesUnsplashfromanimagedownload.(APIrequirement)
            :paramurl:thedownload_urloftheimagetobenotified

            Thismethodwon'treturnanything.Thisendpointshouldjustbe
            pingedwithasimpleGETrequestforUnsplashtoincrementtheimage
            viewcounter.
        '''
        try:
            ifnoturl.startswith('https://api.unsplash.com/photos/'):
                raiseException(_("ERROR:UnknownUnsplashnotifyURL!"))
            access_key=self._get_access_key()
            requests.get(url,params=url_encode({'client_id':access_key}))
        exceptExceptionase:
            logger.exception("Unsplashdownloadnotificationfailed:"+str(e))

    #------------------------------------------------------
    #addunsplashimageurl
    #------------------------------------------------------
    @http.route('/web_unsplash/attachment/add',type='json',auth='user',methods=['POST'])
    defsave_unsplash_url(self,unsplashurls=None,**kwargs):
        """
            unsplashurls={
                image_id1:{
                    url:image_url,
                    download_url:download_url,
                },
                image_id2:{
                    url:image_url,
                    download_url:download_url,
                },
                .....
            }
        """
        defslugify(s):
            '''Keepsonlyalphanumericcharacters,hyphensandspacesfromastring.
                Thestringwillalsobetruncatedto1024charactersmax.
                :params:thestringtobefiltered
                :return:thesanitizedstring
            '''
            return"".join([cforcinsifc.isalnum()orcinlist("-")])[:1024]

        ifnotunsplashurls:
            return[]

        uploads=[]
        Attachments=request.env['ir.attachment']

        query=kwargs.get('query','')
        query=slugify(query)

        res_model=kwargs.get('res_model','ir.ui.view')
        ifres_model!='ir.ui.view'andkwargs.get('res_id'):
            res_id=int(kwargs['res_id'])
        else:
            res_id=None

        forkey,valueinunsplashurls.items():
            url=value.get('url')
            try:
                ifnoturl.startswith(('https://images.unsplash.com/','https://plus.unsplash.com/')):
                    logger.exception("ERROR:UnknownUnsplashURL!:"+url)
                    raiseException(_("ERROR:UnknownUnsplashURL!"))
                req=requests.get(url)
                ifreq.status_code!=requests.codes.ok:
                    continue

                #getmime-typeofimageurlbecauseunsplashurldosn'tcontainsmime-typesinurl
                image_base64=base64.b64encode(req.content)
            exceptrequests.exceptions.ConnectionErrorase:
                logger.exception("ConnectionError:"+str(e))
                continue
            exceptrequests.exceptions.Timeoutase:
                logger.exception("Timeout:"+str(e))
                continue

            image_base64=tools.image_process(image_base64,verify_resolution=True)
            mimetype=guess_mimetype(base64.b64decode(image_base64))
            #appendimageextensioninname
            query+=mimetypes.guess_extension(mimetype)or''

            #/unsplash/5gR788gfd/lion
            url_frags=['unsplash',key,query]

            attachment=Attachments.create({
                'name':'_'.join(url_frags),
                'url':'/'+'/'.join(url_frags),
                'mimetype':mimetype,
                'datas':image_base64,
                'public':res_model=='ir.ui.view',
                'res_id':res_id,
                'res_model':res_model,
                'description':value.get('description'),
            })
            attachment.generate_access_token()
            uploads.append(attachment._get_media_info())

            #NotifiesUnsplashfromanimagedownload.(APIrequirement)
            self._notify_download(value.get('download_url'))

        returnuploads

    @http.route("/web_unsplash/fetch_images",type='json',auth="user")
    deffetch_unsplash_images(self,**post):
        access_key=self._get_access_key()
        app_id=self.get_unsplash_app_id()
        ifnotaccess_keyornotapp_id:
            return{'error':'key_not_found'}
        post['client_id']=access_key
        response=requests.get('https://api.unsplash.com/search/photos/',params=url_encode(post))
        ifresponse.status_code==requests.codes.ok:
            returnresponse.json()
        else:
            return{'error':response.status_code}

    @http.route("/web_unsplash/get_app_id",type='json',auth="public")
    defget_unsplash_app_id(self,**post):
        returnrequest.env['ir.config_parameter'].sudo().get_param('unsplash.app_id')

    @http.route("/web_unsplash/save_unsplash",type='json',auth="user")
    defsave_unsplash(self,**post):
        ifrequest.env.user._has_unsplash_key_rights(mode='write'):
            request.env['ir.config_parameter'].sudo().set_param('unsplash.app_id',post.get('appId'))
            request.env['ir.config_parameter'].sudo().set_param('unsplash.access_key',post.get('key'))
            returnTrue
        raisewerkzeug.exceptions.NotFound()
