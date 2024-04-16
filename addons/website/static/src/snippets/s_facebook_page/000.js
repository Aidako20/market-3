flectra.define('website.s_facebook_page',function(require){
'usestrict';

varpublicWidget=require('web.public.widget');
varutils=require('web.utils');

constFacebookPageWidget=publicWidget.Widget.extend({
    selector:'.o_facebook_page',
    disabledInEditableMode:false,

    /**
     *@override
     */
    start:function(){
        vardef=this._super.apply(this,arguments);

        constparams=_.pick(this.$el.data(),'href','id','height','tabs','small_header','hide_cover','show_facepile');
        if(!params.href){
            returndef;
        }
        if(params.id){
            params.href=`https://www.facebook.com/${params.id}`;
        }
        deleteparams.id;
        params.width=utils.confine(Math.floor(this.$el.width()),180,500);

        varsrc=$.param.querystring('https://www.facebook.com/plugins/page.php',params);
        this.$iframe=$('<iframe/>',{
            src:src,
            class:'o_temp_auto_element',
            width:params.width,
            height:params.height,
            css:{
                border:'none',
                overflow:'hidden',
            },
            scrolling:'no',
            frameborder:'0',
            allowTransparency:'true',
        });
        this.$el.append(this.$iframe);

        returndef;
    },
    /**
     *@override
     */
    destroy:function(){
        this._super.apply(this,arguments);

        if(this.$iframe){
            this.$iframe.remove();
        }
    },
});

publicWidget.registry.facebookPage=FacebookPageWidget;

returnFacebookPageWidget;
});
