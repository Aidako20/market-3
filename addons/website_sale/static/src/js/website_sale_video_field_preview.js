flectra.define('website_sale.video_field_preview',function(require){
"usestrict";


varAbstractField=require('web.AbstractField');
varcore=require('web.core');
varfieldRegistry=require('web.field_registry');

varQWeb=core.qweb;

/**
 *Displayspreviewofthevideoshowcasingproduct.
 */
varFieldVideoPreview=AbstractField.extend({
    className:'d-blocko_field_video_preview',

    _render:function(){
        this.$el.html(QWeb.render('productVideo',{
            embedCode:this.value,
        }));
    },
});

fieldRegistry.add('video_preview',FieldVideoPreview);

returnFieldVideoPreview;

});
