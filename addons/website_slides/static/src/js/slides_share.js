flectra.define('website_slides.slides_share',function(require){
'usestrict';

varpublicWidget=require('web.public.widget');
require('website_slides.slides');
varcore=require('web.core');
var_t=core._t;

varShareMail=publicWidget.Widget.extend({
    events:{
        'clickbutton':'_sendMail',
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _sendMail:function(){
        varself=this;
        varinput=this.$('input');
        varslideID=this.$('button').data('slide-id');
        if(input.val()&&input[0].checkValidity()){
            this.$el.removeClass('o_has_error').find('.form-control,.custom-select').removeClass('is-invalid');
            this._rpc({
                route:'/slides/slide/send_share_email',
                params:{
                    slide_id:slideID,
                    email:input.val(),
                },
            }).then(function(){
                self.$el.html($('<divclass="alertalert-info"role="alert">'+_t('<strong>Thankyou!</strong>Mailhasbeensent.')+'</div>'));
            });
        }else{
            this.$el.addClass('o_has_error').find('.form-control,.custom-select').addClass('is-invalid');
            input.focus();
        }
    },
});

publicWidget.registry.websiteSlidesShare=publicWidget.Widget.extend({
    selector:'#wrapwrap',
    events:{
        'clicka.o_wslides_js_social_share':'_onSlidesSocialShare',
        'click.o_clipboard_button':'_onShareLinkCopy',
    },

    /**
     *@override
     *@param{Object}parent
     */
    start:function(parent){
        vardefs=[this._super.apply(this,arguments)];
        defs.push(newShareMail(this).attachTo($('.oe_slide_js_share_email')));

        returnPromise.all(defs);
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@override
     *@param{Object}ev
     */
    _onSlidesSocialShare:function(ev){
        ev.preventDefault();
        varpopUpURL=$(ev.currentTarget).attr('href');
        varpopUp=window.open(popUpURL,'ShareDialog','width=626,height=436');
        $(window).on('focus',function(){
            if(popUp.closed){
                $(window).off('focus');
            }
        });
    },

    _onShareLinkCopy:function(ev){
        ev.preventDefault();
        var$clipboardBtn=$(ev.currentTarget);
        $clipboardBtn.tooltip({title:"Copied!",trigger:"manual",placement:"bottom"});
        varself=this;
        varclipboard=newClipboardJS('#'+$clipboardBtn[0].id,{
            target:function(){
                varshare_link_el=self.$('#wslides_share_link_id_'+$clipboardBtn[0].id.split('id_')[1]);
                returnshare_link_el[0];
            },
            container:this.el
        });
        clipboard.on('success',function(){
            clipboard.destroy();
            $clipboardBtn.tooltip('show');
            _.delay(function(){
                $clipboardBtn.tooltip("hide");
            },800);
        });
        clipboard.on('error',function(e){
            console.log(e);
            clipboard.destroy();
        })
    },
});
});
