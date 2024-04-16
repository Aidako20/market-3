flectra.define('website_slides.course.enroll',function(require){
'usestrict';

varcore=require('web.core');
varDialog=require('web.Dialog');
varpublicWidget=require('web.public.widget');
var_t=core._t;

varSlideEnrollDialog=Dialog.extend({
    template:'slide.course.join.request',

    init:function(parent,options,modalOptions){
        modalOptions=_.defaults(modalOptions||{},{
            title:_t('RequestAccess.'),
            size:'medium',
            buttons:[{
                text:_t('Yes'),
                classes:'btn-primary',
                click:this._onSendRequest.bind(this)
            },{
                text:_t('Cancel'),
                close:true
            }]
        });
        this.$element=options.$element;
        this.channelId=options.channelId;
        this._super(parent,modalOptions);
    },

    _onSendRequest:function(){
        varself=this;
        this._rpc({
            model:'slide.channel',
            method:'action_request_access',
            args:[self.channelId]
        }).then(function(result){
            if(result.error){
                self.$element.replaceWith('<divclass="alertalert-danger"role="alert"><strong>'+result.error+'</strong></div>');
            }elseif(result.done){
                self.$element.replaceWith('<divclass="alertalert-success"role="alert"><strong>'+_t('Requestsent!')+'</strong></div>');
            }else{
                self.$element.replaceWith('<divclass="alertalert-danger"role="alert"><strong>'+_t('Unknownerror,tryagain.')+'</strong></div>');
            }
            self.close();
        });
    }
    
});

publicWidget.registry.websiteSlidesEnroll=publicWidget.Widget.extend({
    selector:'.o_wslides_js_channel_enroll',
    xmlDependencies:['/website_slides/static/src/xml/slide_course_join.xml'],
    events:{
        'click':'_onSendRequestClick',
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------
    
    _openDialog:function(channelId){
        newSlideEnrollDialog(this,{
            channelId:channelId,
            $element:this.$el
        }).open();
    },
    
    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------
    
    _onSendRequestClick:function(ev){
        ev.preventDefault();
        this._openDialog($(ev.currentTarget).data('channelId'));
    }
});

return{
    slideEnrollDialog:SlideEnrollDialog,
    websiteSlidesEnroll:publicWidget.registry.websiteSlidesEnroll
};

});
