flectra.define('web.Menu',function(require){
"usestrict";

varAppsMenu=require('web.AppsMenu');
varconfig=require('web.config');
varcore=require('web.core');
vardom=require('web.dom');
varSystrayMenu=require('web.SystrayMenu');
varUserMenu=require('web.UserMenu');
varWidget=require('web.Widget');

UserMenu.prototype.sequence=0;//forceUserMenutobetheright-mostiteminthesystray
SystrayMenu.Items.push(UserMenu);

varQWeb=core.qweb;

varMenu=Widget.extend({
    template:'Menu',
    menusTemplate:'Menu.sections',
    events:{
        'mouseover.o_menu_sections>li:not(.show)':'_onMouseOverMenu',
        'click.o_menu_brand':'_onAppNameClicked',
    },

    init:function(parent,menu_data){
        varself=this;
        this._super.apply(this,arguments);

        this.$menu_sections={};
        this.menu_data=menu_data;

        //Preparenavbar'smenus
        var$menu_sections=$(QWeb.render(this.menusTemplate,{
            menu_data:this.menu_data,
        }));
        $menu_sections.filter('section').each(function(){
            self.$menu_sections[parseInt(this.className,10)]=$(this).children('li');
        });

        //Busevent
        core.bus.on('change_menu_section',this,this.change_menu_section);
    },
    start:function(){
        varself=this;

        this.$menu_apps=this.$('.o_menu_apps');
        this.$menu_brand_placeholder=this.$('.o_menu_brand');
        this.$section_placeholder=this.$('.o_menu_sections');
        this._updateMenuBrand();

        //Navbar'smenuseventhandlers
        varon_secondary_menu_click=function(ev){
            ev.preventDefault();
            varmenu_id=$(ev.currentTarget).data('menu');
            varaction_id=$(ev.currentTarget).data('action-id');
            self._on_secondary_menu_click(menu_id,action_id);
        };
        varmenu_ids=_.keys(this.$menu_sections);
        varprimary_menu_id,$section;
        for(vari=0;i<menu_ids.length;i++){
            primary_menu_id=menu_ids[i];
            $section=this.$menu_sections[primary_menu_id];
            $section.on('click','a[data-menu]',self,on_secondary_menu_click.bind(this));
        }

        //AppsMenu
        this._appsMenu=newAppsMenu(self,this.menu_data);
        varappsMenuProm=this._appsMenu.appendTo(this.$menu_apps);

        //SystrayMenu
        this.systray_menu=newSystrayMenu(this);
        varsystrayMenuProm=this.systray_menu.attachTo(this.$('.o_menu_systray')).then(function(){
            self.systray_menu.on_attach_callback(); //Atthispoint,weknowweareintheDOM
            dom.initAutoMoreMenu(self.$section_placeholder,{
            maxWidth:function(){
                returnself.$el.width()-(self.$menu_apps.outerWidth(true)+self.$menu_brand_placeholder.outerWidth(true)+self.systray_menu.$el.outerWidth(true));
            },
            sizeClass:'SM',
            });
        });



        returnPromise.all([this._super.apply(this,arguments),appsMenuProm,systrayMenuProm]);
    },
    change_menu_section:function(primary_menu_id){
        if(!this.$menu_sections[primary_menu_id]){
            this._updateMenuBrand();
            return;//unknownmenu_id
        }

        if(this.current_primary_menu===primary_menu_id){
            return;//alreadyinthatmenu
        }

        if(this.current_primary_menu){
            this.$menu_sections[this.current_primary_menu].detach();
        }

        //Getbacktheapplicationname
        for(vari=0;i<this.menu_data.children.length;i++){
            if(this.menu_data.children[i].id===primary_menu_id){
                this._updateMenuBrand(this.menu_data.children[i].name);
                break;
            }
        }

        this.$menu_sections[primary_menu_id].appendTo(this.$section_placeholder);
        this.current_primary_menu=primary_menu_id;

        core.bus.trigger('resize');
    },
    _trigger_menu_clicked:function(menu_id,action_id){
        this.trigger_up('menu_clicked',{
            id:menu_id,
            action_id:action_id,
            previous_menu_id:this.current_secondary_menu||this.current_primary_menu,
        });
    },
    /**
     *UpdatesthenameoftheappinthemenutothevalueofbrandName.
     *IfbrandNameisfalsy,hidesthemenuanditssections.
     *
     *@private
     *@param{brandName}string
     */
    _updateMenuBrand:function(brandName){
        if(brandName){
            this.$menu_brand_placeholder.text(brandName).show();
            this.$section_placeholder.show();
        }else{
            this.$menu_brand_placeholder.hide()
            this.$section_placeholder.hide();
        }
    },
    _on_secondary_menu_click:function(menu_id,action_id){
        varself=this;

        //Itisstillpossiblethatwedon'thaveanaction_id(forexample,menutoggler)
        if(action_id){
            self._trigger_menu_clicked(menu_id,action_id);
            this.current_secondary_menu=menu_id;
        }
    },
    /**
     *Helpersusedbyweb_clientinordertorestorethestatefrom
     *anurl(byrestore,readre-synchronizemenuandactionmanager)
     */
    action_id_to_primary_menu_id:function(action_id){
        varprimary_menu_id,found;
        for(vari=0;i<this.menu_data.children.length&&!primary_menu_id;i++){
            found=this._action_id_in_subtree(this.menu_data.children[i],action_id);
            if(found){
                primary_menu_id=this.menu_data.children[i].id;
            }
        }
        returnprimary_menu_id;
    },
    _action_id_in_subtree:function(root,action_id){
        //action_idcanbeastringoraninteger
        if(root.action&&root.action.split(',')[1]===String(action_id)){
            returntrue;
        }
        varfound;
        for(vari=0;i<root.children.length&&!found;i++){
            found=this._action_id_in_subtree(root.children[i],action_id);
        }
        returnfound;
    },
    menu_id_to_action_id:function(menu_id,root){
        if(!root){
            root=$.extend(true,{},this.menu_data);
        }

        if(root.id===menu_id){
            returnroot.action.split(',')[1];
        }
        for(vari=0;i<root.children.length;i++){
            varaction_id=this.menu_id_to_action_id(menu_id,root.children[i]);
            if(action_id!==undefined){
                returnaction_id;
            }
        }
        returnundefined;
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Returnstheidofthecurrentprimary(firstlevel)menu.
     *
     *@returns{integer}
     */
    getCurrentPrimaryMenu:function(){
        returnthis.current_primary_menu;
    },
    /**
     *Openthefirstapp,returnswhetheranapplicationwasfound.
     *
     *@returns{Boolean}
     */
    openFirstApp:function(){
        returnthis._appsMenu.openFirstApp();
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Whenclickingonappname,opensthefirstactionoftheapp
     *
     *@private
     *@param{MouseEvent}ev
     */
    _onAppNameClicked:function(ev){
        varactionID=parseInt(this.menu_id_to_action_id(this.current_primary_menu));
        this._trigger_menu_clicked(this.current_primary_menu,actionID);
    },
    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onMouseOverMenu:function(ev){
        if(config.device.isMobile){
            return;
        }
        var$target=$(ev.currentTarget);
        var$opened=$target.siblings('.show');
        if($opened.length){
            $opened.find('[data-toggle="dropdown"]:first').dropdown('toggle');
            $opened.removeClass('show');
            $target.find('[data-toggle="dropdown"]:first').dropdown('toggle');
            $target.addClass('show');
        }
    },
});

returnMenu;

});
