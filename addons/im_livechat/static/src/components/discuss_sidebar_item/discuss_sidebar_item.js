flectra.define('im_livechat/static/src/components/discuss_sidebar_item/discuss_sidebar_item.js',function(require){
'usestrict';

constcomponents={
    DiscussSidebarItem:require('mail/static/src/components/discuss_sidebar_item/discuss_sidebar_item.js'),
};

const{patch}=require('web.utils');

patch(components.DiscussSidebarItem,'im_livechat/static/src/components/discuss_sidebar_item/discuss_sidebar_item.js',{

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    hasUnpin(...args){
        constres=this._super(...args);
        returnres||this.thread.channel_type==='livechat';
    }

});

});
