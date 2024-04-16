flectra.define('website_slides.ratingField',function(require){
"usestrict";

varbasicFields=require('web.basic_fields');
varfieldRegistry=require('web.field_registry');

varcore=require('web.core');

varQWeb=core.qweb;

varFieldFloatRating=basicFields.FieldFloat.extend({
    xmlDependencies:!basicFields.FieldFloat.prototype.xmlDependencies?
        ['/portal_rating/static/src/xml/portal_tools.xml']:basicFields.FieldFloat.prototype.xmlDependencies.concat(
            ['/portal_rating/static/src/xml/portal_tools.xml']
        ),
    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     *@private
     */
    _render:function(){
        varself=this;

        returnPromise.resolve(this._super()).then(function(){
            self.$el.html(QWeb.render('portal_rating.rating_stars_static',{
                'val':self.value/2,
                'inline_mode':true
            }));
        });
    },
});

fieldRegistry.add('field_float_rating',FieldFloatRating);

return{
    FieldFloatRating:FieldFloatRating,
};

});
