flectra.define('options.s_google_map_options',function(require){
'usestrict';

const{_t}=require('web.core');
constoptions=require('web_editor.snippets.options');

options.registry.GoogleMap=options.Class.extend({

    //--------------------------------------------------------------------------
    //Options
    //--------------------------------------------------------------------------

    /**
     *@seethis.selectClassforparameters
     */
    resetMapColor(previewMode,widgetValue,params){
        this.$target[0].dataset.mapColor='';
    },
    /**
     *@seethis.selectClassforparameters
     */
    setFormattedAddress(previewMode,widgetValue,params){
        this.$target[0].dataset.pinAddress=params.gmapPlace.formatted_address;
    },
    /**
     *@seethis.selectClassforparameters
     */
    asyncshowDescription(previewMode,widgetValue,params){
        constdescriptionEl=this.$target[0].querySelector('.description');
        if(widgetValue&&!descriptionEl){
            this.$target.append($(`
                <divclass="description">
                    <font>${_t('Visitus:')}</font>
                    <span>${_t('OurofficeislocatedinthenortheastofBrussels.TEL(555)4322365')}</span>
                </div>`)
            );
        }elseif(!widgetValue&&descriptionEl){
            descriptionEl.remove();
        }
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    _computeWidgetState(methodName,params){
        if(methodName==='showDescription'){
            returnthis.$target[0].querySelector('.description')?'true':'';
        }
        returnthis._super(...arguments);
    },
});
});
