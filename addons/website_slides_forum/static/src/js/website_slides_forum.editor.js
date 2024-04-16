flectra.define('website_slides_forum.editor',function(require){
"usestrict";

varcore=require('web.core');
varQWeb=core.qweb;
varWebsiteNewMenu=require('website.newMenu');

 WebsiteNewMenu.include({
    xmlDependencies:WebsiteNewMenu.prototype.xmlDependencies.concat(
        ['/website_slides_forum/static/src/xml/website_slides_forum_channel.xml']
    ),
});
});
