flectra.define('web.FavoriteMenu',function(require){
    "usestrict";

    constDialog=require('web.OwlDialog');
    constDropdownMenu=require('web.DropdownMenu');
    const{FACET_ICONS}=require("web.searchUtils");
    constRegistry=require('web.Registry');
    const{useModel}=require('web/static/src/js/model.js');

    /**
     *'Favorites'menu
     *
     *Simplerenderingofthefiltersoftype`favorites`givenbythecontrolpanel
     *model.ItusesmostofthebehavioursimplementedbythedropdownmenuComponent,
     *withtheadditionofasubmenuregistryusedtodisplayadditionalcomponents.
     *Onlythefavoritegenerator(@seeCustomFavoriteItem)isregisteredin
     *the`web`module.
     *@seeDropdownMenuforadditionaldetails.
     *@extendsDropdownMenu
     */
    classFavoriteMenuextendsDropdownMenu{
        constructor(){
            super(...arguments);

            this.model=useModel('searchModel');
            this.state.deletedFavorite=false;
        }

        //---------------------------------------------------------------------
        //Getters
        //---------------------------------------------------------------------

        /**
         *@override
         */
        geticon(){
            returnFACET_ICONS.favorite;
        }
        getdialogTitle(){
            returnthis.env._t("Warning");
        }
        /**
         *@override
         */
        getitems(){
            constfavorites=this.model.get('filters',f=>f.type==='favorite');
            constregistryMenus=this.constructor.registry.values().reduce(
                (menus,Component)=>{
                    if(Component.shouldBeDisplayed(this.env)){
                        menus.push({
                            key:Component.name,
                            groupNumber:Component.groupNumber,
                            Component,
                        });
                    }
                    returnmenus;
                },
                []
            );
            return[...favorites,...registryMenus];
        }

        /**
         *@override
         */
        gettitle(){
            returnthis.env._t("Favorites");
        }

        //---------------------------------------------------------------------
        //Handlers
        //---------------------------------------------------------------------

        /**
         *@private
         *@param{OwlEvent}ev
         */
        _onItemRemoved(ev){
            constfavorite=this.items.find(fav=>fav.id===ev.detail.item.id);
            this.state.deletedFavorite=favorite;
        }

        /**
         *@private
         *@param{OwlEvent}ev
         */
        _onItemSelected(ev){
            ev.stopPropagation();
            this.model.dispatch('toggleFilter',ev.detail.item.id);
        }

        /**
         *@private
         */
        async_onRemoveFavorite(){
            this.model.dispatch('deleteFavorite',this.state.deletedFavorite.id);
            this.state.deletedFavorite=false;
        }
    }

    FavoriteMenu.registry=newRegistry();

    FavoriteMenu.components=Object.assign({},DropdownMenu.components,{
        Dialog,
    });
    FavoriteMenu.template='web.FavoriteMenu';

    returnFavoriteMenu;
});
