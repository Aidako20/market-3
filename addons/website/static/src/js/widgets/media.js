flectra.define('website.widgets.media',function(require){
'usestrict';

const{ImageWidget}=require('wysiwyg.widgets.media');

ImageWidget.include({
    _getAttachmentsDomain(){
        constdomain=this._super(...arguments);
        domain.push('|',['url','=',false],'!',['url','=like','/web/image/website.%']);
        domain.push(['key','=',false]);
        returndomain;
    }
});
});
