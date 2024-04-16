#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importio
importlogging
importre
importtime
importrequests
importwerkzeug.wrappers
fromPILimportImage,ImageFont,ImageDraw
fromlxmlimportetree
frombase64importb64decode,b64encode

fromflectra.httpimportrequest
fromflectraimporthttp,tools,_,SUPERUSER_ID
fromflectra.addons.http_routing.models.ir_httpimportslug
fromflectra.exceptionsimportUserError
fromflectra.modules.moduleimportget_module_path,get_resource_path
fromflectra.tools.miscimportfile_open

from..models.ir_attachmentimportSUPPORTED_IMAGE_MIMETYPES

logger=logging.getLogger(__name__)
DEFAULT_LIBRARY_ENDPOINT='https://media-api.flectrahq.com'

classWeb_Editor(http.Controller):
    #------------------------------------------------------
    #convertfontintopicture
    #------------------------------------------------------
    @http.route([
        '/web_editor/font_to_img/<icon>',
        '/web_editor/font_to_img/<icon>/<color>',
        '/web_editor/font_to_img/<icon>/<color>/<int:size>',
        '/web_editor/font_to_img/<icon>/<color>/<int:size>/<int:alpha>',
        ],type='http',auth="none")
    defexport_icon_to_png(self,icon,color='#000',size=100,alpha=255,font='/web/static/lib/fontawesome/fonts/fontawesome-webfont.ttf'):
        """Thismethodconvertsanunicodecharactertoanimage(usingFont
            Awesomefontbydefault)andisusedonlyformassmailingbecause
            customfontsarenotsupportedinmail.
            :paramicon:decimalencodingofunicodecharacter
            :paramcolor:RGBcodeofthecolor
            :paramsize:Pixelsininteger
            :paramalpha:transparencyoftheimagefrom0to255
            :paramfont:fontpath

            :returnsPNGimageconvertedfromgivenfont
        """
        #Makesurewehaveatleastsize=1
        size=max(1,min(size,512))
        #Initializefont
        withtools.file_open(font.lstrip('/'),'rb')asf:
            font_obj=ImageFont.truetype(f,size)

        #ifreceivedcharacterisnotanumber,keepoldbehaviour(iconischaracter)
        icon=chr(int(icon))ificon.isdigit()elseicon

        #Determinethedimensionsoftheicon
        image=Image.new("RGBA",(size,size),color=(0,0,0,0))
        draw=ImageDraw.Draw(image)

        boxw,boxh=draw.textsize(icon,font=font_obj)
        draw.text((0,0),icon,font=font_obj)
        left,top,right,bottom=image.getbbox()

        #Createanalphamask
        imagemask=Image.new("L",(boxw,boxh),0)
        drawmask=ImageDraw.Draw(imagemask)
        drawmask.text((-left,-top),icon,font=font_obj,fill=alpha)

        #Createasolidcolorimageandapplythemask
        ifcolor.startswith('rgba'):
            color=color.replace('rgba','rgb')
            color=','.join(color.split(',')[:-1])+')'
        iconimage=Image.new("RGBA",(boxw,boxh),color)
        iconimage.putalpha(imagemask)

        #Createoutputimage
        outimage=Image.new("RGBA",(boxw,size),(0,0,0,0))
        outimage.paste(iconimage,(left,top))

        #outputimage
        output=io.BytesIO()
        outimage.save(output,format="PNG")
        response=werkzeug.wrappers.Response()
        response.mimetype='image/png'
        response.data=output.getvalue()
        response.headers['Cache-Control']='public,max-age=604800'
        response.headers['Access-Control-Allow-Origin']='*'
        response.headers['Access-Control-Allow-Methods']='GET,POST'
        response.headers['Connection']='close'
        response.headers['Date']=time.strftime("%a,%d-%b-%Y%TGMT",time.gmtime())
        response.headers['Expires']=time.strftime("%a,%d-%b-%Y%TGMT",time.gmtime(time.time()+604800*60))

        returnresponse

    #------------------------------------------------------
    #Updateachecklistintheeditoroncheck/uncheck
    #------------------------------------------------------
    @http.route('/web_editor/checklist',type='json',auth='user')
    defupdate_checklist(self,res_model,res_id,filename,checklistId,checked,**kwargs):
        record=request.env[res_model].browse(res_id)
        value=filenameinrecord._fieldsandrecord[filename]
        htmlelem=etree.fromstring("<div>%s</div>"%value,etree.HTMLParser())
        checked=bool(checked)

        li=htmlelem.find(".//li[@id='checklist-id-"+str(checklistId)+"']")

        ifnotliornotself._update_checklist_recursive(li,checked,children=True,ancestors=True):
            returnvalue

        value=etree.tostring(htmlelem[0][0],encoding='utf-8',method='html')[5:-6]
        record.write({filename:value})

        returnvalue

    def_update_checklist_recursive(self,li,checked,children=False,ancestors=False):
        if'checklist-id-'notinli.get('id',''):
            returnFalse

        classname=li.get('class','')
        if('o_checked'inclassname)==checked:
            returnFalse

        #check/uncheck
        ifchecked:
            classname='%so_checked'%classname
        else:
            classname=re.sub(r"\s?o_checked\s?",'',classname)
        li.set('class',classname)

        #propagatetochildren
        ifchildren:
            node=li.getnext()
            ul=None
            ifnodeisnotNone:
                ifnode.tag=='ul':
                    ul=node
                ifnode.tag=='li'andlen(node.getchildren())==1andnode.getchildren()[0].tag=='ul':
                    ul=node.getchildren()[0]

            ifulisnotNone:
                forchildinul.getchildren():
                    ifchild.tag=='li':
                        self._update_checklist_recursive(child,checked,children=True)

        #propagatetoancestors
        ifancestors:
            allSelected=True
            ul=li.getparent()
            iful.tag=='li':
                ul=ul.getparent()

            forchildinul.getchildren():
                ifchild.tag=='li'and'checklist-id'inchild.get('id','')and'o_checked'notinchild.get('class',''):
                    allSelected=False

            node=ul.getprevious()
            ifnodeisNone:
                node=ul.getparent().getprevious()
            ifnodeisnotNoneandnode.tag=='li':
                self._update_checklist_recursive(node,allSelected,ancestors=True)

        returnTrue

    @http.route('/web_editor/attachment/add_data',type='json',auth='user',methods=['POST'],website=True)
    defadd_data(self,name,data,quality=0,width=0,height=0,res_id=False,res_model='ir.ui.view',generate_access_token=False,**kwargs):
        try:
            data=tools.image_process(data,size=(width,height),quality=quality,verify_resolution=True)
        exceptUserError:
            pass #notanimage
        self._clean_context()
        attachment=self._attachment_create(name=name,data=data,res_id=res_id,res_model=res_model,generate_access_token=generate_access_token)
        returnattachment._get_media_info()

    @http.route('/web_editor/attachment/add_url',type='json',auth='user',methods=['POST'],website=True)
    defadd_url(self,url,res_id=False,res_model='ir.ui.view',**kwargs):
        self._clean_context()
        attachment=self._attachment_create(url=url,res_id=res_id,res_model=res_model)
        returnattachment._get_media_info()

    @http.route('/web_editor/attachment/remove',type='json',auth='user',website=True)
    defremove(self,ids,**kwargs):
        """Removesaweb-basedimageattachmentifitisusedbynoview(template)

        Returnsadictmappingattachmentswhichwouldnotberemoved(ifany)
        mappedtotheviewspreventingtheirremoval
        """
        self._clean_context()
        Attachment=attachments_to_remove=request.env['ir.attachment']
        Views=request.env['ir.ui.view']

        #viewsblockingremovaloftheattachment
        removal_blocked_by={}

        forattachmentinAttachment.browse(ids):
            #in-documentURLsarehtml-escaped,astraightsearchwillnot
            #findthem
            url=tools.html_escape(attachment.local_url)
            views=Views.search([
                "|",
                ('arch_db','like','"%s"'%url),
                ('arch_db','like',"'%s'"%url)
            ])

            ifviews:
                removal_blocked_by[attachment.id]=views.read(['name'])
            else:
                attachments_to_remove+=attachment
        ifattachments_to_remove:
            attachments_to_remove.unlink()
        returnremoval_blocked_by

    @http.route('/web_editor/get_image_info',type='json',auth='user',website=True)
    defget_image_info(self,src=''):
        """Thisrouteisusedtodeterminetheoriginalofanattachmentsothat
        itcanbeusedasabasetomodifyitagain(crop/optimization/filters).
        """
        attachment=None
        id_match=re.search('^/web/image/([^/?]+)',src)
        ifid_match:
            url_segment=id_match.group(1)
            number_match=re.match('^(\d+)',url_segment)
            if'.'inurl_segment:#xml-id
                attachment=request.env['ir.http']._xmlid_to_obj(request.env,url_segment)
            elifnumber_match:#numericid
                attachment=request.env['ir.attachment'].browse(int(number_match.group(1)))
        else:
            #Findattachmentbyurl.Therecanbemultiplematchesbecauseofdefault
            #snippetimagesreferencingthesameimagein/static/,sowelimitto1
            attachment=request.env['ir.attachment'].search([
                ('url','=like',src),
                ('mimetype','in',SUPPORTED_IMAGE_MIMETYPES),
            ],limit=1)
        ifnotattachment:
            return{
                'attachment':False,
                'original':False,
            }
        return{
            'attachment':attachment.read(['id'])[0],
            'original':(attachment.original_idorattachment).read(['id','image_src','mimetype'])[0],
        }

    def_attachment_create(self,name='',data=False,url=False,res_id=False,res_model='ir.ui.view',generate_access_token=False):
        """Createandreturnanewattachment."""
        ifname.lower().endswith('.bmp'):
            #Avoidmismatchbetweencontenttypeandmimetype,seecommitmsg
            name=name[:-4]

        ifnotnameandurl:
            name=url.split("/").pop()

        ifres_model!='ir.ui.view'andres_id:
            res_id=int(res_id)
        else:
            res_id=False

        attachment_data={
            'name':name,
            'public':res_model=='ir.ui.view',
            'res_id':res_id,
            'res_model':res_model,
        }

        ifdata:
            attachment_data['datas']=data
        elifurl:
            attachment_data.update({
                'type':'url',
                'url':url,
            })
        else:
            raiseUserError(_("Youneedtospecifyeitherdataorurltocreateanattachment."))

        attachment=request.env['ir.attachment'].create(attachment_data)
        ifgenerate_access_token:
            attachment.generate_access_token()

        returnattachment

    def_clean_context(self):
        #avoidallowed_company_idswhichmayerroneouslyrestrictbasedonwebsite
        context=dict(request.context)
        context.pop('allowed_company_ids',None)
        request.context=context

    @http.route("/web_editor/get_assets_editor_resources",type="json",auth="user",website=True)
    defget_assets_editor_resources(self,key,get_views=True,get_scss=True,get_js=True,bundles=False,bundles_restriction=[],only_user_custom_files=True):
        """
        Transmittheresourcestheassetseditorneedstowork.

        Params:
            key(str):thekeyoftheviewtheresourcesarerelatedto

            get_views(bool,default=True):
                Trueiftheviewsmustbefetched

            get_scss(bool,default=True):
                Trueifthestylemustbefetched

            get_js(bool,default=True):
                Trueifthejavascriptmustbefetched

            bundles(bool,default=False):
                Trueifthebundlesviewsmustbefetched

            bundles_restriction(list,default=[]):
                Namesofthebundlesinwhichtolookforscssfiles
                (ifempty,searchinallofthem)

            only_user_custom_files(bool,default=True):
                Trueifonlyusercustomfilesmustbefetched

        Returns:
            dict:views,scss,js
        """
        #Relatedviewsmustbefetchediftheuserwantstheviewsand/orthestyle
        views=request.env["ir.ui.view"].with_context(no_primary_children=True,__views_get_original_hierarchy=[]).get_related_views(key,bundles=bundles)
        views=views.read(['name','id','key','xml_id','arch','active','inherit_id'])

        scss_files_data_by_bundle=[]
        js_files_data_by_bundle=[]

        ifget_scss:
            scss_files_data_by_bundle=self._load_resources('scss',views,bundles_restriction,only_user_custom_files)
        ifget_js:
            js_files_data_by_bundle=self._load_resources('js',views,bundles_restriction,only_user_custom_files)

        return{
            'views':get_viewsandviewsor[],
            'scss':get_scssandscss_files_data_by_bundleor[],
            'js':get_jsandjs_files_data_by_bundleor[],
        }

    def_load_resources(self,file_type,views,bundles_restriction,only_user_custom_files):
        AssetsUtils=request.env['web_editor.assets']

        files_data_by_bundle=[]
        resources_type_info={'t_call_assets_attribute':'t-js','mimetype':'text/javascript'}
        iffile_type=='scss':
            resources_type_info={'t_call_assets_attribute':'t-css','mimetype':'text/scss'}

        #Compileregexoutsideoftheloop
        #Thiswillusedtoexcludelibraryscssfilesfromtheresult
        excluded_url_matcher=re.compile("^(.+/lib/.+)|(.+import_bootstrap.+\.scss)$")

        #Firstcheckthet-call-assetsusedintherelatedviews
        url_infos=dict()
        forvinviews:
            forasset_call_nodeinetree.fromstring(v["arch"]).xpath("//t[@t-call-assets]"):
                ifasset_call_node.get(resources_type_info['t_call_assets_attribute'])=="false":
                    continue
                asset_name=asset_call_node.get("t-call-assets")

                #Loopthroughbundlefilestosearchforfileinfo
                files_data=[]
                forfile_infoinrequest.env["ir.qweb"]._get_asset_content(asset_name,{})[0]:
                    iffile_info["atype"]!=resources_type_info['mimetype']:
                        continue
                    url=file_info["url"]

                    #Excludelibraryfiles(seeregexabove)
                    ifexcluded_url_matcher.match(url):
                        continue

                    #Checkifthefileiscustomizedandgetbundle/pathinfo
                    file_data=AssetsUtils.get_asset_info(url)
                    ifnotfile_data:
                        continue

                    #Saveinfoaccordingtothefilter(archwillbefetchedlater)
                    url_infos[url]=file_data

                    if'/user_custom_'inurl\
                            orfile_data['customized']\
                            orfile_type=='scss'andnotonly_user_custom_files:
                        files_data.append(url)

                #scssdataisreturnedsortedbybundle,withthebundles
                #namesandxmlids
                iflen(files_data):
                    files_data_by_bundle.append([
                        {'xmlid':asset_name,'name':request.env.ref(asset_name).name},
                        files_data
                    ])

        #Filterbundles/files:
        #-Afilewhichappearsinmultiplebundlesonlyappearsinthe
        #  firstone(thefirstintheDOM)
        #-Onlykeepbundleswithfileswhichappearsintheaskedbundles
        #  andonlykeepthosefiles
        foriinrange(0,len(files_data_by_bundle)):
            bundle_1=files_data_by_bundle[i]
            forjinrange(0,len(files_data_by_bundle)):
                bundle_2=files_data_by_bundle[j]
                #Inunwantedbundles,keeponlythefileswhichareinwantedbundlestoo(_assets_helpers)
                ifbundle_1[0]["xmlid"]notinbundles_restrictionandbundle_2[0]["xmlid"]inbundles_restriction:
                    bundle_1[1]=[item_1foritem_1inbundle_1[1]ifitem_1inbundle_2[1]]
        foriinrange(0,len(files_data_by_bundle)):
            bundle_1=files_data_by_bundle[i]
            forjinrange(i+1,len(files_data_by_bundle)):
                bundle_2=files_data_by_bundle[j]
                #Ineverybundle,keeponlythefileswhichwerenotfound
                #inpreviousbundles
                bundle_2[1]=[item_2foritem_2inbundle_2[1]ifitem_2notinbundle_1[1]]

        #Onlykeepbundleswhichstillhavefilesandthatwererequested
        files_data_by_bundle=[
            datafordatainfiles_data_by_bundle
            if(len(data[1])>0and(notbundles_restrictionordata[0]["xmlid"]inbundles_restriction))
        ]

        #Fetchthearchofeachkeptfile,ineachbundle
        urls=[]
        forbundle_datainfiles_data_by_bundle:
            urls+=bundle_data[1]
        custom_attachments=AssetsUtils.get_all_custom_attachments(urls)

        forbundle_datainfiles_data_by_bundle:
            foriinrange(0,len(bundle_data[1])):
                url=bundle_data[1][i]
                url_info=url_infos[url]

                content=AssetsUtils.get_asset_content(url,url_info,custom_attachments)

                bundle_data[1][i]={
                    'url':"/%s/%s"%(url_info["module"],url_info["resource_path"]),
                    'arch':content,
                    'customized':url_info["customized"],
                }

        returnfiles_data_by_bundle

    @http.route("/web_editor/save_asset",type="json",auth="user",website=True)
    defsave_asset(self,url,bundle_xmlid,content,file_type):
        """
        Saveagivenmodificationofascss/jsfile.

        Params:
            url(str):
                theoriginalurlofthescss/jsfilewhichhastobemodified

            bundle_xmlid(str):
                thexmlidofthebundleinwhichthescss/jsfileadditioncan
                befound

            content(str):thenewcontentofthescss/jsfile

            file_type(str):'scss'or'js'
        """
        request.env['web_editor.assets'].save_asset(url,bundle_xmlid,content,file_type)

    @http.route("/web_editor/reset_asset",type="json",auth="user",website=True)
    defreset_asset(self,url,bundle_xmlid):
        """
        Thereset_assetrouteisinchargeofrevertingallthechangesthat
        weredonetoascss/jsfile.

        Params:
            url(str):
                theoriginalURLofthescss/jsfiletoreset

            bundle_xmlid(str):
                thexmlidofthebundleinwhichthescss/jsfileadditioncan
                befound
        """
        request.env['web_editor.assets'].reset_asset(url,bundle_xmlid)

    @http.route("/web_editor/public_render_template",type="json",auth="public",website=True)
    defpublic_render_template(self,args):
        #args[0]:xmlidofthetemplatetorender
        #args[1]:optionaldictofrenderingvalues,onlytrustedkeysaresupported
        len_args=len(args)
        assertlen_args>=1andlen_args<=2,'NeedaxmlIDandpotentialrenderingvaluestorenderatemplate'

        trusted_value_keys=('debug',)

        xmlid=args[0]
        values=len_args>1andargs[1]or{}

        View=request.env['ir.ui.view']
        ifxmlidinrequest.env['web_editor.assets']._get_public_asset_xmlids():
            #Forwhitelistedassets,bypassaccessverification
            #TODOinmasterthispartshouldberemovedandsimplyusethe
            #publicgroupontherelatedviewsinstead.Andthenletthenormal
            #flowhandletherendering.
            returnView.sudo()._render_template(xmlid,{k:values[k]forkinvaluesifkintrusted_value_keys})
        #Otherwiseusenormalflow
        returnView.render_public_asset(xmlid,{k:values[k]forkinvaluesifkintrusted_value_keys})

    @http.route('/web_editor/modify_image/<model("ir.attachment"):attachment>',type="json",auth="user",website=True)
    defmodify_image(self,attachment,res_model=None,res_id=None,name=None,data=None,original_id=None):
        """
        Createsamodifiedcopyofanattachmentandreturnsitsimage_srctobe
        insertedintotheDOM.
        """
        fields={
            'original_id':attachment.id,
            'datas':data,
            'type':'binary',
            'res_model':res_modelor'ir.ui.view',
        }
        iffields['res_model']=='ir.ui.view':
            fields['res_id']=0
        elifres_id:
            fields['res_id']=res_id
        ifname:
            fields['name']=name
        attachment=attachment.copy(fields)
        ifattachment.url:
            #Don'tkeepurlifmodifyingstaticattachmentbecausestaticimages
            #areonlyservedfromdiskanddon'tfallbacktoattachments.
            ifre.match(r'^/\w+/static/',attachment.url):
                attachment.url=None
            #Uniquifyurlbyaddingapathsegmentwiththeidbeforethename.
            #Thisallowsustokeeptheunsplashurlformatsoitstillreacts
            #totheunsplashbeacon.
            else:
                url_fragments=attachment.url.split('/')
                url_fragments.insert(-1,str(attachment.id))
                attachment.url='/'.join(url_fragments)
        ifattachment.public:
            returnattachment.image_src
        attachment.generate_access_token()
        return'%s?access_token=%s'%(attachment.image_src,attachment.access_token)

    @http.route(['/web_editor/shape/<module>/<path:filename>'],type='http',auth="public",website=True)
    defshape(self,module,filename,**kwargs):
        """
        Returnsacolor-customizedsvg(backgroundshapeorillustration).
        """
        svg=None
        ifmodule=='illustration':
            attachment=request.env['ir.attachment'].sudo().search([('url','=',request.httprequest.path),('public','=',True)],limit=1)
            ifnotattachment:
                raisewerkzeug.exceptions.NotFound()
            svg=b64decode(attachment.datas).decode('utf-8')
        else:
            shape_path=get_resource_path(module,'static','shapes',filename)
            ifnotshape_path:
                raisewerkzeug.exceptions.NotFound()
            withtools.file_open(shape_path,'r')asfile:
                svg=file.read()

        user_colors=[]
        forkey,valueinkwargs.items():
            colorMatch=re.match('^c([1-5])$',key)
            ifcolorMatch:
                #Checkthatcolorishexorrgb(a)topreventarbitraryinjection
                ifnotre.match(r'(?i)^#[0-9A-F]{6,8}$|^rgba?\(\d{1,3},\d{1,3},\d{1,3}(?:,[0-9.]{1,4})?\)$',value.replace('','')):
                    raisewerkzeug.exceptions.BadRequest()
                user_colors.append([tools.html_escape(value),colorMatch.group(1)])
            elifkey=='flip':
                ifvalue=='x':
                    svg=svg.replace('<svg','<svgstyle="transform:scaleX(-1);"',1)
                elifvalue=='y':
                    svg=svg.replace('<svg','<svgstyle="transform:scaleY(-1)"',1)
                elifvalue=='xy':
                    svg=svg.replace('<svg','<svgstyle="transform:scale(-1)"',1)

        default_palette={
            '1':'#3AADAA',
            '2':'#7C6576',
            '3':'#F6F6F6',
            '4':'#FFFFFF',
            '5':'#383E45',
        }
        color_mapping={default_palette[palette_number]:colorforcolor,palette_numberinuser_colors}
        #createacase-insensitiveregextomatchallthecolorstoreplace,eg:'(?i)(#3AADAA)|(#7C6576)'
        regex='(?i)%s'%'|'.join('(%s)'%colorforcolorincolor_mapping.keys())

        defsubber(match):
            key=match.group().upper()
            returncolor_mapping[key]ifkeyincolor_mappingelsekey
        svg=re.sub(regex,subber,svg)

        returnrequest.make_response(svg,[
            ('Content-type','image/svg+xml'),
            ('Cache-control','max-age=%s'%http.STATIC_CACHE_LONG),
        ])

    @http.route(['/web_editor/media_library_search'],type='json',auth="user",website=True)
    defmedia_library_search(self,**params):
        ICP=request.env['ir.config_parameter'].sudo()
        endpoint=ICP.get_param('web_editor.media_library_endpoint',DEFAULT_LIBRARY_ENDPOINT)
        params['dbuuid']=ICP.get_param('database.uuid')
        response=requests.post('%s/media-library/1/search'%endpoint,data=params)
        ifresponse.status_code==requests.codes.okandresponse.headers['content-type']=='application/json':
            returnresponse.json()
        else:
            return{'error':response.status_code}

    @http.route('/web_editor/save_library_media',type='json',auth='user',methods=['POST'])
    defsave_library_media(self,media):
        """
        Savesimagesfromthemedialibraryasnewattachments,makingthem
        dynamicSVGsifneeded.
            media={
                <media_id>:{
                    'query':'spaceseparatedsearchterms',
                    'is_dynamic_svg':True/False,
                },...
            }
        """
        attachments=[]
        ICP=request.env['ir.config_parameter'].sudo()
        library_endpoint=ICP.get_param('web_editor.media_library_endpoint',DEFAULT_LIBRARY_ENDPOINT)

        media_ids=','.join(media.keys())
        params={
            'dbuuid':ICP.get_param('database.uuid'),
            'media_ids':media_ids,
        }
        response=requests.post('%s/media-library/1/download_urls'%library_endpoint,data=params)
        ifresponse.status_code!=requests.codes.ok:
            raiseException(_("ERROR:couldn'tgetdownloadurlsfrommedialibrary."))

        forid,urlinresponse.json().items():
            req=requests.get(url)
            name='_'.join([media[id]['query'],url.split('/')[-1]])
            #Needtobypasssecuritychecktowriteimagewithmimetypeimage/svg+xml
            #okbecausesvgscomefromwhitelistedorigin
            context={'binary_field_real_user':request.env['res.users'].sudo().browse([SUPERUSER_ID])}
            attachment=request.env['ir.attachment'].sudo().with_context(context).create({
                'name':name,
                'mimetype':req.headers['content-type'],
                'datas':b64encode(req.content),
                'public':True,
                'res_model':'ir.ui.view',
                'res_id':0,
            })
            ifmedia[id]['is_dynamic_svg']:
                attachment['url']='/web_editor/shape/illustration/%s'%slug(attachment)
            attachments.append(attachment._get_media_info())

        returnattachments
