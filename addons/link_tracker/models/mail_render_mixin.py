#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importre

fromhtmlimportunescape
fromwerkzeugimporturls

fromflectraimportapi,models,tools


classMailRenderMixin(models.AbstractModel):
    _inherit="mail.render.mixin"

    #------------------------------------------------------------
    #TOOLS
    #------------------------------------------------------------

    @api.model
    def_shorten_links(self,html,link_tracker_vals,blacklist=None,base_url=None):
        """Shortenlinksinanhtmlcontent.Itusesthe'/r'shortURLrouting
        introducedinthismodule.UsingthestandardFlectraregexlocallinksare
        foundandreplacedbyglobalURLs(notincludingmailto,tel,sms).

        TDEFIXME:couldbegreattohavearecordtoenablewebsite-basedURLs

        :paramlink_tracker_vals:valuesgiventothecreatedlink.tracker,containing
          forexample:campaign_id,medium_id,source_id,andanyotherrelevantfields
          likemass_mailing_idinmass_mailing;
        :paramlistblacklist:listof(local)URLstonotshorten(e.g.
          '/unsubscribe_from_list')
        :paramstrbase_url:eithergiven,eitherbasedonconfigparameter

        :return:updatedhtml
        """
        base_url=base_urlorself.env['ir.config_parameter'].sudo().get_param('web.base.url')
        short_schema=base_url+'/r/'
        formatchinre.findall(tools.HTML_TAG_URL_REGEX,html):
            href=match[0]
            long_url=match[1]
            label=(match[3]or'').strip()

            ifnotblacklistornot[sforsinblacklistifsinlong_url]andnotlong_url.startswith(short_schema):
                create_vals=dict(link_tracker_vals,url=unescape(long_url),label=unescape(label))
                link=self.env['link.tracker'].create(create_vals)
                iflink.short_url:
                    new_href=href.replace(long_url,link.short_url)
                    html=html.replace(href,new_href)

        returnhtml

    @api.model
    def_shorten_links_text(self,content,link_tracker_vals,blacklist=None,base_url=None):
        """Shortenlinksinastringcontent.Workslike``_shorten_links``but
        targettingstringcontent,nothtml.

        :return:updatedcontent
        """
        ifnotcontent:
            returncontent
        base_url=base_urlorself.env['ir.config_parameter'].sudo().get_param('web.base.url')
        shortened_schema=base_url+'/r/'
        unsubscribe_schema=base_url+'/sms/'
        fororiginal_urlinre.findall(tools.TEXT_URL_REGEX,content):
            #don'tshortenalready-shortenedlinksorlinkstowardsunsubscribepage
            iforiginal_url.startswith(shortened_schema)ororiginal_url.startswith(unsubscribe_schema):
                continue
            #supportblacklistitemsinpath,like/u/
            parsed=urls.url_parse(original_url,scheme='http')
            ifblacklistandany(iteminparsed.pathforiteminblacklist):
                continue

            create_vals=dict(link_tracker_vals,url=unescape(original_url))
            link=self.env['link.tracker'].create(create_vals)
            iflink.short_url:
                content=content.replace(original_url,link.short_url,1)

        returncontent
