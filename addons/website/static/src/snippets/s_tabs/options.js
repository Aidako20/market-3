flectra.define('website.s_tabs_options',function(require){
'usestrict';

constoptions=require('web_editor.snippets.options');

options.registry.NavTabs=options.Class.extend({
    isTopOption:true,

    /**
     *@override
     */
    start:function(){
        this._findLinksAndPanes();
        returnthis._super.apply(this,arguments);
    },
    /**
     *@override
     */
    onBuilt:function(){
        this._generateUniqueIDs();
    },
    /**
     *@override
     */
    onClone:function(){
        this._generateUniqueIDs();
    },

    //--------------------------------------------------------------------------
    //Options
    //--------------------------------------------------------------------------

    /**
     *Createsanewtabandtab-pane.
     *
     *@seethis.selectClassforparameters
     */
    addTab:function(previewMode,widgetValue,params){
        var$activeItem=this.$navLinks.filter('.active').parent();
        var$activePane=this.$tabPanes.filter('.active');

        var$navItem=$activeItem.clone();
        var$navLink=$navItem.find('.nav-link').removeClass('activeshow');
        var$tabPane=$activePane.clone().removeClass('activeshow');
        $navItem.insertAfter($activeItem);
        $tabPane.insertAfter($activePane);
        this._findLinksAndPanes();
        this._generateUniqueIDs();

        $navLink.tab('show');
    },
    /**
     *Removesthecurrentactivetabanditscontent.
     *
     *@seethis.selectClassforparameters
     */
    removeTab:function(previewMode,widgetValue,params){
        varself=this;

        var$activeLink=this.$navLinks.filter('.active');
        var$activePane=this.$tabPanes.filter('.active');

        var$next=this.$navLinks.eq((this.$navLinks.index($activeLink)+1)%this.$navLinks.length);

        returnnewPromise(resolve=>{
            $next.one('shown.bs.tab',function(){
                $activeLink.parent().remove();
                $activePane.remove();
                self._findLinksAndPanes();
                resolve();
            });
            $next.tab('show');
        });
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    _computeWidgetVisibility:asyncfunction(widgetName,params){
        if(widgetName==='remove_tab_opt'){
            return(this.$tabPanes.length>2);
        }
        returnthis._super(...arguments);
    },
    /**
     *@private
     */
    _findLinksAndPanes:function(){
        this.$navLinks=this.$target.find('.nav:first.nav-link');
        this.$tabPanes=this.$target.find('.tab-content:first.tab-pane');
    },
    /**
     *@private
     */
    _generateUniqueIDs:function(){
        for(vari=0;i<this.$navLinks.length;i++){
            varid=_.now()+'_'+_.uniqueId();
            varidLink='nav_tabs_link_'+id;
            varidContent='nav_tabs_content_'+id;
            this.$navLinks.eq(i).attr({
                'id':idLink,
                'href':'#'+idContent,
                'aria-controls':idContent,
            });
            this.$tabPanes.eq(i).attr({
                'id':idContent,
                'aria-labelledby':idLink,
            });
        }
    },
});
options.registry.NavTabsStyle=options.Class.extend({

    //--------------------------------------------------------------------------
    //Options
    //--------------------------------------------------------------------------

    /**
     *Setthestyleofthetabs.
     *
     *@seethis.selectClassforparameters
     */
    setStyle:function(previewMode,widgetValue,params){
        const$nav=this.$target.find('.s_tabs_nav:first.nav');
        constisPills=widgetValue==='pills';
        $nav.toggleClass('nav-tabscard-header-tabs',!isPills);
        $nav.toggleClass('nav-pills',isPills);
        this.$target.find('.s_tabs_nav:first').toggleClass('card-header',!isPills).toggleClass('mb-3',isPills);
        this.$target.toggleClass('card',!isPills);
        this.$target.find('.s_tabs_content:first').toggleClass('card-body',!isPills);
    },
    /**
     *Horizontal/verticalnav.
     *
     *@seethis.selectClassforparameters
     */
    setDirection:function(previewMode,widgetValue,params){
        constisVertical=widgetValue==='vertical';
        this.$target.toggleClass('rows_col_no_resizes_col_no_bgcolor',isVertical);
        this.$target.find('.s_tabs_nav:first.nav').toggleClass('flex-column',isVertical);
        this.$target.find('.s_tabs_nav:first>.nav-link').toggleClass('py-2',isVertical);
        this.$target.find('.s_tabs_nav:first').toggleClass('col-md-3',isVertical);
        this.$target.find('.s_tabs_content:first').toggleClass('col-md-9',isVertical);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    _computeWidgetState:function(methodName,params){
        switch(methodName){
            case'setStyle':
                returnthis.$target.find('.s_tabs_nav:first.nav').hasClass('nav-pills')?'pills':'tabs';
            case'setDirection':
                returnthis.$target.find('.s_tabs_nav:first.nav').hasClass('flex-column')?'vertical':'horizontal';
        }
        returnthis._super(...arguments);
    },
});
});
