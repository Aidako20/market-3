flectra.define('website.mobile',function(require){
'usestrict';

varcore=require('web.core');
varDialog=require('web.Dialog');
varwebsiteNavbarData=require('website.navbar');

var_t=core._t;

varMobilePreviewDialog=Dialog.extend({
    /**
     *Tweaksthemodalsothatitappearsasaphoneandmodifiestheiframe
     *renderingtoshowmoreaccuratemobileview.
     *
     *@override
     */
    start:function(){
        varself=this;
        this.$modal.addClass('oe_mobile_preview');
        this.$modal.on('click','.modal-header',function(){
            self.$el.toggleClass('o_invert_orientation');
        });
        this.$iframe=$('<iframe/>',{
            id:'mobile-viewport',
            src:$.param.querystring(window.location.href,'mobilepreview'),
        });
        this.$iframe.on('load',function(e){
            self.$iframe.contents().find('body').removeClass('o_connected_user');
            self.$iframe.contents().find('#oe_main_menu_navbar').remove();
        });
        this.$iframe.appendTo(this.$el);

        returnthis._super.apply(this,arguments);
    },
});

varMobileMenu=websiteNavbarData.WebsiteNavbarActionWidget.extend({
    actions:_.extend({},websiteNavbarData.WebsiteNavbarActionWidget.prototype.actions||{},{
        'show-mobile-preview':'_onMobilePreviewClick',
    }),

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Calledwhenthemobileactionistriggered->instantiatethemobile
     *previewdialog.
     *
     *@private
     */
    _onMobilePreviewClick:function(){
        if(this.mobilePreview&&!this.mobilePreview.isDestroyed()){
            returnthis.mobilePreview.close();
        }
        this.mobilePreview=newMobilePreviewDialog(this,{
            title:_t('Mobilepreview')+'<spanclass="fafa-refresh"/>',
        }).open();
    },
});

websiteNavbarData.websiteNavbarRegistry.add(MobileMenu,'#mobile-menu');

return{
    MobileMenu:MobileMenu,
    MobilePreviewDialog:MobilePreviewDialog,
};
});
