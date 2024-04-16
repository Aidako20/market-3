#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64
importos
importre
importuuid

fromlxmlimportetree

fromflectraimportmodels
fromflectra.toolsimportmisc
fromflectra.addons.base.models.assetsbundleimportEXTENSIONS

_match_asset_file_url_regex=re.compile("^/(\w+)/(.+?)(\.custom\.(.+))?\.(\w+)$")


classAssets(models.AbstractModel):
    _name='web_editor.assets'
    _description='AssetsUtils'

    defget_all_custom_attachments(self,urls):
        """
        Fetchalltheir.attachmentrecordsrelatedtogivenURLs.

        Params:
            urls(str[]):listofurls

        Returns:
            ir.attachment():attachmentrecordsrelatedtothegivenURLs.
        """
        returnself._get_custom_attachment(urls,op='in')

    defget_asset_content(self,url,url_info=None,custom_attachments=None):
        """
        Fetchthecontentofanasset(scss/js)file.Thatcontentiseither
        theoneoftherelatedfileonthediskortheoneofthecorresponding
        customir.attachmentrecord.

        Params:
            url(str):theURLoftheasset(scss/js)file/ir.attachment

            url_info(dict,optional):
                therelatedurlinfo(seeget_asset_info)(allowstooptimize
                somecodewhichalreadyhavetheinfoanddonotwantthis
                functiontore-getit)

            custom_attachments(ir.attachment(),optional):
                therelatedcustomir.attachmentrecordsthefunctionmightneed
                tosearchinto(allowstooptimizesomecodewhichalreadyhave
                thatinfoanddonotwantthisfunctiontore-getit)

        Returns:
            utf-8encodedcontentoftheasset(scss/js)
        """
        ifurl_infoisNone:
            url_info=self.get_asset_info(url)

        ifurl_info["customized"]:
            #Ifthefileisalreadycustomized,thecontentisfoundinthe
            #correspondingattachment
            attachment=None
            ifcustom_attachmentsisNone:
                attachment=self._get_custom_attachment(url)
            else:
                attachment=custom_attachments.filtered(lambdar:r.url==url)
            returnattachmentandbase64.b64decode(attachment.datas)orFalse

        #Ifthefileisnotyetcustomized,thecontentisfoundbyreading
        #thelocalfile
        withmisc.file_open(url.strip('/'),'rb',filter_ext=EXTENSIONS)asf:
            returnf.read()

    defget_asset_info(self,url):
        """
        Returninformationaboutanasset(scss/js)file/ir.attachmentjustby
        lookingatitsURL.

        Params:
            url(str):theurloftheasset(scss/js)file/ir.attachment

        Returns:
            dict:
                module(str):theoriginalasset'srelatedapp

                resource_path(str):
                    therelativepathtotheoriginalassetfromtherelatedapp

                customized(bool):whethertheassetisacustomizedoneornot

                bundle(str):
                    thenameofthebundletheassetcustomizes(Falseifthis
                    isnotacustomizedasset)
        """
        m=_match_asset_file_url_regex.match(url)
        ifnotm:
            returnFalse
        return{
            'module':m.group(1),
            'resource_path':"%s.%s"%(m.group(2),m.group(5)),
            'customized':bool(m.group(3)),
            'bundle':m.group(4)orFalse
        }

    defmake_custom_asset_file_url(self,url,bundle_xmlid):
        """
        ReturnthecustomizedversionofanassetURL,thatistheURLtheasset
        wouldhaveifitwascustomized.

        Params:
            url(str):theoriginalasset'surl
            bundle_xmlid(str):thenameofthebundletheassetwouldcustomize

        Returns:
            str:theURLthegivenassetwouldhaveifitwascustomizedinthe
                 givenbundle
        """
        parts=url.rsplit(".",1)
        return"%s.custom.%s.%s"%(parts[0],bundle_xmlid,parts[1])

    defreset_asset(self,url,bundle_xmlid):
        """
        Deletethepotentialcustomizationsmadetoagiven(original)asset.

        Params:
            url(str):theURLoftheoriginalasset(scss/js)file

            bundle_xmlid(str):
                thenameofthebundleinwhichthecustomizationstodelete
                weremade
        """
        custom_url=self.make_custom_asset_file_url(url,bundle_xmlid)

        #Simplydeletetheattachementwhichcontainsthemodifiedscss/jsfile
        #andthexpathviewwhichlinksit
        self._get_custom_attachment(custom_url).unlink()
        self._get_custom_view(custom_url).unlink()

    defsave_asset(self,url,bundle_xmlid,content,file_type):
        """
        Customizethecontentofagivenasset(scss/js).

        Params:
            url(src):
                theURLoftheoriginalassettocustomize(whetherornotthe
                assetwasalreadycustomized)

            bundle_xmlid(src):
                thenameofthebundleinwhichthecustomizationswilltake
                effect

            content(src):thenewcontentoftheasset(scss/js)

            file_type(src):
                either'scss'or'js'accordingtothefilebeingcustomized
        """
        custom_url=self.make_custom_asset_file_url(url,bundle_xmlid)
        datas=base64.b64encode((contentor"\n").encode("utf-8"))

        #Checkifthefiletosavehadalreadybeenmodified
        custom_attachment=self._get_custom_attachment(custom_url)
        ifcustom_attachment:
            #Ifitwasalreadymodified,simplyoverridethecorresponding
            #attachmentcontent
            custom_attachment.write({"datas":datas})
        else:
            #Ifnot,createanewattachmenttocopytheoriginalscss/jsfile
            #content,withitsmodifications
            new_attach={
                'name':url.split("/")[-1],
                'type':"binary",
                'mimetype':(file_type=='js'and'text/javascript'or'text/scss'),
                'datas':datas,
                'url':custom_url,
            }
            new_attach.update(self._save_asset_attachment_hook())
            self.env["ir.attachment"].create(new_attach)

            #Createaviewtoextendthetemplatewhichaddstheoriginalfile
            #tolinkthenewmodifiedversioninstead
            file_type_info={
                'tag':'link'iffile_type=='scss'else'script',
                'attribute':'href'iffile_type=='scss'else'src',
            }

            defviews_linking_url(view):
                """
                Returnswhethertheviewarchhassomehtmltaglinkedto
                theurl.(note:searchingfortheURLstringisnotenoughasit
                couldappearinacommentoranxpathexpression.)
                """
                tree=etree.XML(view.arch)
                returnbool(tree.xpath("//%%(tag)s[@%%(attribute)s='%(url)s']"%{
                    'url':url,
                }%file_type_info))

            IrUiView=self.env["ir.ui.view"]
            view_to_xpath=IrUiView.get_related_views(bundle_xmlid,bundles=True).filtered(views_linking_url)
            new_view={
                'name':custom_url,
                'key':'web_editor.%s_%s'%(file_type,str(uuid.uuid4())[:6]),
                'mode':"extension",
                'inherit_id':view_to_xpath.id,
                'arch':"""
                    <datainherit_id="%(inherit_xml_id)s"name="%(name)s">
                        <xpathexpr="//%%(tag)s[@%%(attribute)s='%(url_to_replace)s']"position="attributes">
                            <attributename="%%(attribute)s">%(new_url)s</attribute>
                        </xpath>
                    </data>
                """%{
                    'inherit_xml_id':view_to_xpath.xml_id,
                    'name':custom_url,
                    'url_to_replace':url,
                    'new_url':custom_url,
                }%file_type_info
            }
            new_view.update(self._save_asset_view_hook())
            IrUiView.create(new_view)

        self.env["ir.qweb"].clear_caches()

    def_get_custom_attachment(self,custom_url,op='='):
        """
        Fetchtheir.attachmentrecordrelatedtothegivencustomizedasset.

        Params:
            custom_url(str):theURLofthecustomizedasset
            op(str,default:'='):theoperatortousetosearchtherecords

        Returns:
            ir.attachment()
        """
        assertopin('in','='),'Invalidoperator'
        returnself.env["ir.attachment"].search([("url",op,custom_url)])

    def_get_custom_view(self,custom_url,op='='):
        """
        Fetchtheir.ui.viewrecordrelatedtothegivencustomizedasset(the
        inheritingviewwhichreplacetheoriginalassetbythecustomizedone).

        Params:
            custom_url(str):theURLofthecustomizedasset
            op(str,default:'='):theoperatortousetosearchtherecords

        Returns:
            ir.ui.view()
        """
        assertopin('='),'Invalidoperator'
        returnself.env["ir.ui.view"].search([("name",op,custom_url)])

    def_save_asset_attachment_hook(self):
        """
        ReturnstheadditionalvaluestousetowritetheDBoncustomized
        attachmentcreation.

        Returns:
            dict
        """
        return{}

    def_save_asset_view_hook(self):
        """
        ReturnstheadditionalvaluestousetowritetheDBoncustomized
        asset'srelatedviewcreation.

        Returns:
            dict
        """
        return{}

    def_get_public_asset_xmlids(self):
        return["web_editor.compiled_assets_wysiwyg"]
