flectra.define('website_event.set_customize_options',function(require){
"usestrict";

varCustomizeMenu=require('website.customizeMenu');
varpublicWidget=require('web.public.widget');

varEventSpecificOptions=publicWidget.Widget.extend({
    template:'website_event.customize_options',
    xmlDependencies:['/website_event/static/src/xml/customize_options.xml'],
    events:{
        'change#display-website-menu':'_onDisplaySubmenuChange',
    },

    /**
     *@override
     */
    start:function(){
        this.$submenuInput=this.$('#display-website-menu');
        this.modelName=this._getEventObject().model;
        this.eventId=this._getEventObject().id;
        this._initCheckbox();
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    _onDisplaySubmenuChange:function(ev){
        varcheckboxValue=this.$submenuInput.is(':checked');
        this._toggleSubmenuDisplay(checkboxValue);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    _getCheckboxFields:function(){
        return['website_menu','website_url'];
    },

    _getCheckboxFieldMatch:function(checkboxField){
        if(checkboxField==='website_menu'){
            returnthis.$submenuInput;
        }
    },

    _getEventObject:function(){
        varrepr=$('html').data('main-object');
        varm=repr.match(/(.+)\((\d+),(.*)\)/);
        return{
            model:m[1],
            id:m[2]|0,
        };
    },

    _initCheckbox:function(){
        varself=this;
        this._rpc({
            model:this.modelName,
            method:'read',
            args:[
                [this.eventId],
                this._getCheckboxFields()
            ],
        }).then((data)=>{
            self._initCheckboxCallback(data);
        });
    },

    _initCheckboxCallback:function(rpcData){
        if(rpcData[0]['website_menu']){
            varsubmenuInput=this._getCheckboxFieldMatch('website_menu');
            submenuInput.attr('checked','checked');
        }
        this.eventUrl=rpcData[0]['website_url'];
    },

    _reloadEventPage:function(){
        window.location=this.eventUrl;
    },

    _toggleSubmenuDisplay:function(val){
        varself=this;
        this._rpc({
            model:this.modelName,
            method:'toggle_website_menu',
            args:[[this.eventId],val],
        }).then(function(){
            self._reloadEventPage();
        });
    },

});

CustomizeMenu.include({
    _getEventObject:function(){
        varrepr=$('html').data('main-object');
        varm=repr.match(/(.+)\((\d+),(.*)\)/);
        return{
            model:m[1],
            id:m[2]|0,
        };
    },

    _loadCustomizeOptions:function(){
        varself=this;
        vardef=this._super.apply(this,arguments);
        returndef.then(function(){
            if(!self.__eventOptionsLoaded&&self._getEventObject().model==='event.event'){
                self.__eventOptionsLoaded=true;
                self.eventOptions=newEventSpecificOptions(self);
                //Ifthisisthefirstcustomizemenu,addthedividerattop
                if(!self.$('.dropdown-divider').length){
                    self.$('.dropdown-menu').append($('<div/>',{
                        class:'dropdown-divider',
                        role:'separator',
                    }));
                }
                self.eventOptions.insertAfter(self.$el.find('.dropdown-divider:first()'));
            }
        });
    },
});

return{
    EventSpecificOptions:EventSpecificOptions,
};

});
