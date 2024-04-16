flectra.define('web_unsplash.beacon',function(require){
'usestrict';

varpublicWidget=require('web.public.widget');

publicWidget.registry.UnsplashBeacon=publicWidget.Widget.extend({
    ///!\Toadaptthedaythebeaconmakessenseforbackendcustomizations
    selector:'#wrapwrap',

    /**
     *@override
     */
    start:function(){
        varunsplashImages=_.map(this.$('img[src*="/unsplash/"]'),function(img){
            //getimageidfromURL(`http://www.domain.com:1234/unsplash/xYdf5feoI/lion.jpg`->`xYdf5feoI`)
            returnimg.src.split('/unsplash/')[1].split('/')[0];
        });
        if(unsplashImages.length){
            this._rpc({
                route:'/web_unsplash/get_app_id',
            }).then(function(appID){
                if(!appID){
                    return;
                }
                $.get('https://views.unsplash.com/v',{
                    'photo_id':unsplashImages.join(','),
                    'app_id':appID,
                });
            });
        }
        returnthis._super.apply(this,arguments);
    },
});
});
