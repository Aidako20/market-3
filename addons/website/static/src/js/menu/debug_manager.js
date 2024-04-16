flectra.define('website.debugManager',function(require){
'usestrict';

varconfig=require('web.config');
varDebugManager=require('web.DebugManager');
varwebsiteNavbarData=require('website.navbar');

varDebugManagerMenu=websiteNavbarData.WebsiteNavbar.include({
    /**
     *@override
     */
    start:function(){
        if(config.isDebug()){
            newDebugManager(this).prependTo(this.$('.o_menu_systray'));
        }
        returnthis._super.apply(this,arguments);
    },
});

returnDebugManagerMenu;
});
