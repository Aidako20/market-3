flectra.define('website.post_link',function(require){
'usestrict';

constpublicWidget=require('web.public.widget');
constwUtils=require('website.utils');

publicWidget.registry.postLink=publicWidget.Widget.extend({
    selector:'.post_link',
    events:{
        'click':'_onClickPost',
    },

    /**
     *@override
     */
    start(){
        //AllowsthelinktobeinteractedwithonlywhenJavascriptisloaded.
        this.el.classList.add('o_post_link_js_loaded');
        returnthis._super(...arguments);
    },
    /**
     *@override
     */
    destroy(){
        this._super(...arguments);
        this.el.classList.remove('o_post_link_js_loaded');
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    _onClickPost:function(ev){
        ev.preventDefault();
        consturl=this.el.dataset.post||this.el.href;
        letdata={};
        for(let[key,value]ofObject.entries(this.el.dataset)){
            if(key.startsWith('post_')){
                data[key.slice(5)]=value;
            }
        }
        wUtils.sendRequest(url,data);
    },
});

});
