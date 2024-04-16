#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64
importre
importrequests

fromwerkzeug.urlsimporturl_parse

fromflectraimportmodels


classAssets(models.AbstractModel):
    _inherit='web_editor.assets'

    defmake_scss_customization(self,url,values):
        """
        Makesascsscustomizationofthegivenfile.Thatfilemust
        containascssmapincludingalinecommentcontainingtheword'hook',
        toindicatethelocationwheretowritethenewkey,valuepairs.

        Params:
            url(str):
                theURLofthescssfiletocustomize(supposedtobeavariable
                filewhichwillappearintheassets_commonbundle)

            values(dict):
                key,valuemappingtointegrateinthefile'smap(containingthe
                wordhook).Ifakeyisalreadyinthefile'smap,itsvalueis
                overridden.
        """
        IrAttachment=self.env['ir.attachment']
        if'color-palettes-number'invalues:
            self.reset_asset('/website/static/src/scss/options/colors/user_color_palette.scss','web.assets_common')
            #Donotresetallthemecolorsforcompatibility(notremovingalpha->epsiloncolors)
            self.make_scss_customization('/website/static/src/scss/options/colors/user_theme_color_palette.scss',{
                'success':'null',
                'info':'null',
                'warning':'null',
                'danger':'null',
            })

        delete_attachment_id=values.pop('delete-font-attachment-id',None)
        ifdelete_attachment_id:
            delete_attachment_id=int(delete_attachment_id)
            IrAttachment.search([
                '|',('id','=',delete_attachment_id),
                ('original_id','=',delete_attachment_id),
                ('name','like','%google-font%')
            ]).unlink()

        google_local_fonts=values.get('google-local-fonts')
        ifgoogle_local_fontsandgoogle_local_fonts!='null':
            #"('font_x':45,'font_y':'')"->{'font_x':'45','font_y':''}
            google_local_fonts=dict(re.findall(r"'([^']+)':'?(\d*)",google_local_fonts))
            #Googleisservingdifferentfontformat(woff,woff2,ttf,eot..)
            #basedontheuseragent.Weneedtogetthewoff2asthisis
            #supportedbyallthebrowerswesupport.
            headers_woff2={
                'user-agent':'Mozilla/5.0(X11;Linuxx86_64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/101.0.4951.41Safari/537.36',
            }
            forfont_nameingoogle_local_fonts:
                ifgoogle_local_fonts[font_name]:
                    google_local_fonts[font_name]=int(google_local_fonts[font_name])
                else:
                    font_family_attachments=IrAttachment
                    font_content=requests.get(
                        f'https://fonts.googleapis.com/css?family={font_name}&display=swap',
                        timeout=5,headers=headers_woff2,
                    ).content.decode()

                    deffetch_google_font(src):
                        statement=src.group()
                        url,font_format=re.match(r'src:url\(([^\)]+)\)(.+)',statement).groups()
                        req=requests.get(url,timeout=5,headers=headers_woff2)
                        #https://fonts.gstatic.com/s/modak/v18/EJRYQgs1XtIEskMB-hRp7w.woff2
                        #->s-modak-v18-EJRYQgs1XtIEskMB-hRp7w.woff2
                        name=url_parse(url).path.lstrip('/').replace('/','-')
                        attachment=IrAttachment.create({
                            'name':f'google-font-{name}',
                            'type':'binary',
                            'datas':base64.b64encode(req.content),
                            'public':True,
                        })
                        nonlocalfont_family_attachments
                        font_family_attachments+=attachment
                        return'src:url(/web/content/%s/%s)%s'%(
                            attachment.id,
                            name,
                            font_format,
                        )

                    font_content=re.sub(r'src:url\(.+\)',fetch_google_font,font_content)

                    attach_font=IrAttachment.create({
                        'name':f'{font_name}(google-font)',
                        'type':'binary',
                        'datas':base64.encodebytes(font_content.encode()),
                        'mimetype':'text/css',
                        'public':True,
                    })
                    google_local_fonts[font_name]=attach_font.id
                    #Thatfieldismeanttokeeptrackoftheoriginal
                    #imageattachmentwhenanimageisbeingmodified(bythe
                    #websitebuilderforinstance).Itmakessensetouseit
                    #heretolinkfontfamilyattachmenttothemainfont
                    #attachment.Itwilleasetheunlinklater.
                    font_family_attachments.original_id=attach_font.id

            #{'font_x':45,'font_y':55}->"('font_x':45,'font_y':55)"
            values['google-local-fonts']=str(google_local_fonts).replace('{','(').replace('}',')')

        custom_url=self.make_custom_asset_file_url(url,'web.assets_common')
        updatedFileContent=self.get_asset_content(custom_url)orself.get_asset_content(url)
        updatedFileContent=updatedFileContent.decode('utf-8')
        forname,valueinvalues.items():
            #Protectvariablenamessotheycannotbecomputedasnumbers
            #onSCSScompilation(e.g.var(--700)=>var(700)).
            ifisinstance(value,str):
                value=re.sub(
                    r"var\(--([0-9]+)\)",
                    lambdamatchobj:"var(--#{"+matchobj.group(1)+"})",
                    value)
            pattern="'%s':%%s,\n"%name
            regex=re.compile(pattern%".+")
            replacement=pattern%value
            ifregex.search(updatedFileContent):
                updatedFileContent=re.sub(regex,replacement,updatedFileContent)
            else:
                updatedFileContent=re.sub(r'(*)(.*hook.*)',r'\1%s\1\2'%replacement,updatedFileContent)

        #Bundleis'assets_common'asthisrouteisonlymeanttoupdate
        #variablesscssfiles
        self.save_asset(url,'web.assets_common',updatedFileContent,'scss')

    def_get_custom_attachment(self,custom_url,op='='):
        """
        Seeweb_editor.Assets._get_custom_attachment
        Extendtoonlyreturntheattachmentsrelatedtothecurrentwebsite.
        """
        ifself.env.user.has_group('website.group_website_designer'):
            self=self.sudo()
        website=self.env['website'].get_current_website()
        res=super(Assets,self)._get_custom_attachment(custom_url,op=op)
        #FIXME(?)Inwebsite,thoseattachmentsshouldalwayshavebeen
        #createdwithawebsite_id.The"notwebsite_id"partinthefollowing
        #conditionmightthereforebeuseless(especiallysincetheattachments
        #donotseemordered).Itwasdevelopedinthespiritofserved
        #attachmentswhichfollowthisruleof"servewhatbelongstothe
        #currentwebsiteorallthewebsites"butitprobablydoesnotmake
        #sensehere.Ithoweverallowedtodiscoverabugwhereattachments
        #wereleftwithoutwebsite_id.Thiswillbekeptuntouchedinstable
        #butwillbereviewedandmademorerobustinmaster.
        returnres.with_context(website_id=website.id).filtered(lambdax:notx.website_idorx.website_id==website)

    def_get_custom_view(self,custom_url,op='='):
        """
        Seeweb_editor.Assets._get_custom_view
        Extendtoonlyreturntheviewsrelatedtothecurrentwebsite.
        """
        website=self.env['website'].get_current_website()
        res=super(Assets,self)._get_custom_view(custom_url,op=op)
        returnres.with_context(website_id=website.id).filter_duplicate()

    def_save_asset_attachment_hook(self):
        """
        Seeweb_editor.Assets._save_asset_attachment_hook
        ExtendtoaddwebsiteIDatattachmentcreation.
        """
        res=super(Assets,self)._save_asset_attachment_hook()

        website=self.env['website'].get_current_website()
        ifwebsite:
            res['website_id']=website.id
        returnres

    def_save_asset_view_hook(self):
        """
        Seeweb_editor.Assets._save_asset_view_hook
        ExtendtoaddwebsiteIDatviewcreation.
        """
        res=super(Assets,self)._save_asset_view_hook()

        website=self.env['website'].get_current_website()
        ifwebsite:
            res['website_id']=website.id
        returnres
