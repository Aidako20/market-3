flectra.define('website_slides.slide.archive',function(require){
'usestrict';

varpublicWidget=require('web.public.widget');
varDialog=require('web.Dialog');
varcore=require('web.core');
var_t=core._t;

varSlideArchiveDialog=Dialog.extend({
    template:'slides.slide.archive',

    /**
     *@override
     */
    init:function(parent,options){
        options=_.defaults(options||{},{
            title:_t('ArchiveSlide'),
            size:'medium',
            buttons:[{
                text:_t('Archive'),
                classes:'btn-primary',
                click:this._onClickArchive.bind(this)
            },{
                text:_t('Cancel'),
                close:true
            }]
        });

        this.$slideTarget=options.slideTarget;
        this.slideId=this.$slideTarget.data('slideId');
        this._super(parent,options);
    },
    _checkForEmptySections:function(){
        $('.o_wslides_slide_list_category').each(function(){
            var$categoryHeader=$(this).find('.o_wslides_slide_list_category_header');
            varcategorySlideCount=$(this).find('.o_wslides_slides_list_slide:not(.o_not_editable)').length;
            var$emptyFlagContainer=$categoryHeader.find('.o_wslides_slides_list_drag').first();
            var$emptyFlag=$emptyFlagContainer.find('small');
            if(categorySlideCount===0&&$emptyFlag.length===0){
                $emptyFlagContainer.append($('<small>',{
                    'class':"ml-1text-mutedfont-weight-bold",
                    text:_t("(empty)")
                }));
            }
        });
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Calls'archive'onslidecontrollerandthenvisuallyremovestheslidedomelement
     */
    _onClickArchive:function(){
        varself=this;

        this._rpc({
            route:'/slides/slide/archive',
            params:{
                slide_id:this.slideId
            },
        }).then(function(isArchived){
            if(isArchived){
                self.$slideTarget.closest('.o_wslides_slides_list_slide').remove();
                self._checkForEmptySections();
            }
            self.close();
        });
    }
});

publicWidget.registry.websiteSlidesSlideArchive=publicWidget.Widget.extend({
    selector:'.o_wslides_js_slide_archive',
    xmlDependencies:['/website_slides/static/src/xml/slide_management.xml'],
    events:{
        'click':'_onArchiveSlideClick',
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    _openDialog:function($slideTarget){
        newSlideArchiveDialog(this,{slideTarget:$slideTarget}).open();
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{Event}ev
     */
    _onArchiveSlideClick:function(ev){
        ev.preventDefault();
        var$slideTarget=$(ev.currentTarget);
        this._openDialog($slideTarget);
    },
});

return{
    slideArchiveDialog:SlideArchiveDialog,
    websiteSlidesSlideArchive:publicWidget.registry.websiteSlidesSlideArchive
};

});
