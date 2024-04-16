flectra.define('website.iframe_widget',function(require){
"usestrict";


varAbstractField=require('web.AbstractField');
varcore=require('web.core');
varfieldRegistry=require('web.field_registry');

varQWeb=core.qweb;

/**
 *Displayiframe
 */
varFieldIframePreview=AbstractField.extend({
    className:'d-blocko_field_iframe_previewm-0h-100',

    _render:function(){
        this.$el.html(QWeb.render('website.iframeWidget',{
            url:this.value,
        }));
    },
});

fieldRegistry.add('iframe',FieldIframePreview);

returnFieldIframePreview;

});
