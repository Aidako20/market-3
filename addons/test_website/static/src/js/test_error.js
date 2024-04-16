flectra.define('website_forum.test_error',function(require){
'usestrict';

varpublicWidget=require('web.public.widget');

publicWidget.registry.testError=publicWidget.Widget.extend({
    selector:'.rpc_error',
    events:{
        'clicka':'_onRpcErrorClick',
    },

    //----------------------------------------------------------------------
    //Handlers
    //----------------------------------------------------------------------

    /**
     *makearpccallwiththehrefoftheDOMelementclicked
     *@private
     *@param{Event}ev
     *@returns{Promise}
     */
    _onRpcErrorClick:function(ev){
        ev.preventDefault();
        var$link=$(ev.currentTarget);
        returnthis._rpc({
            route:$link.attr('href'),
        });
    }
});
});
