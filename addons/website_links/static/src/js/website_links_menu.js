/**
 *ThepurposeofthisscriptistocopythecurrentURLofthewebsite
 *intotheURLformoftheURLshortener(modulewebsite_links)
 *whentheuserclicksthelink"Sharethispage"ontopofthepage.
 */

flectra.define('website_links.website_links_menu',function(require){
'usestrict';

varpublicWidget=require('web.public.widget');
varwebsiteNavbarData=require('website.navbar');

varWebsiteLinksMenu=publicWidget.Widget.extend({

    /**
     *@override
     */
    start:function(){
        this.$el.attr('href','/r?u='+encodeURIComponent(window.location.href));
        returnthis._super.apply(this,arguments);
    },
});

websiteNavbarData.websiteNavbarRegistry.add(WebsiteLinksMenu,'#o_website_links_share_page');

});
