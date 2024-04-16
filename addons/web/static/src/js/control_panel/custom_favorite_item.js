flectra.define('web.CustomFavoriteItem',function(require){
    "usestrict";

    constDropdownMenuItem=require('web.DropdownMenuItem');
    constFavoriteMenu=require('web.FavoriteMenu');
    const{useAutofocus}=require('web.custom_hooks');
    const{useModel}=require('web/static/src/js/model.js');

    const{useRef}=owl.hooks;

    letfavoriteId=0;

    /**
     *Favoritegeneratormenu
     *
     *Thiscomponentisusedtoaddanewfavoritelinkedwhichwilltakeevery
     *informationoutofthecurrentcontextandsaveittoanew`ir.filter`.
     *
     *Thereare3additionalinputstomodifythefilter:
     *-atextinput(mandatory):thenameofthefavorite(mustbeunique)
     *-'usebydefault'checkbox:ifchecked,thefavoritewillbethedefault
     *                             filterofthecurrentmodel(andwillbypass
     *                             anyexistingdefaultfilter).Cannotbechecked
     *                             alongwith'sharewithallusers'checkbox.
     *-'sharewithallusers'checkbox:ifchecked,thefavoritewillbeavailable
     *                                   withallusersinsteadofthecurrent
     *                                   one.Cannotbecheckedalongwith'use
     *                                   bydefault'checkbox.
     *Finally,thereisa'Save'buttonusedtoapplythecurrentconfiguration
     *andsavethecontexttoanewfilter.
     *@extendsDropdownMenuItem
     */
    classCustomFavoriteItemextendsDropdownMenuItem{
        constructor(){
            super(...arguments);

            constfavId=favoriteId++;
            this.useByDefaultId=`o_favorite_use_by_default_${favId}`;
            this.shareAllUsersId=`o_favorite_share_all_users_${favId}`;

            this.descriptionRef=useRef('description');
            this.model=useModel('searchModel');
            this.interactive=true;
            Object.assign(this.state,{
                description:this.env.action.name||"",
                isDefault:false,
                isShared:false,
            });

            useAutofocus();
        }

        //---------------------------------------------------------------------
        //Private
        //---------------------------------------------------------------------

        /**
         *@private
         */
        _saveFavorite(){
            if(!this.state.description.length){
                this.env.services.notification.notify({
                    message:this.env._t("Anameforyourfavoritefilterisrequired."),
                    type:'danger',
                });
                returnthis.descriptionRef.el.focus();
            }
            constfavorites=this.model.get('filters',f=>f.type==='favorite');
            if(favorites.some(f=>f.description===this.state.description)){
                this.env.services.notification.notify({
                    message:this.env._t("Filterwithsamenamealreadyexists."),
                    type:'danger',
                });
                returnthis.descriptionRef.el.focus();
            }
            this.model.dispatch('createNewFavorite',{
                type:'favorite',
                description:this.state.description,
                isDefault:this.state.isDefault,
                isShared:this.state.isShared,
            });
            //Resetstate
            Object.assign(this.state,{
                description:this.env.action.name||"",
                isDefault:false,
                isShared:false,
                open:false,
            });
        }

        //---------------------------------------------------------------------
        //Handlers
        //---------------------------------------------------------------------

        /**
         *@private
         *@param{Event}evchangeEvent
         */
        _onCheckboxChange(ev){
            const{checked,id}=ev.target;
            if(this.useByDefaultId===id){
                this.state.isDefault=checked;
                if(checked){
                    this.state.isShared=false;
                }
            }else{
                this.state.isShared=checked;
                if(checked){
                    this.state.isDefault=false;
                }
            }
        }

        /**
         *@private
         *@param{jQueryEvent}ev
         */
        _onInputKeydown(ev){
            switch(ev.key){
                case'Enter':
                    ev.preventDefault();
                    this._saveFavorite();
                    break;
                case'Escape':
                    //Givesthefocusbacktothecomponent.
                    ev.preventDefault();
                    ev.target.blur();
                    break;
            }
        }

        //---------------------------------------------------------------------
        //Static
        //---------------------------------------------------------------------

        /**
         *@param{Object}env
         *@returns{boolean}
         */
        staticshouldBeDisplayed(env){
            returntrue;
        }
    }

    CustomFavoriteItem.props={};
    CustomFavoriteItem.template='web.CustomFavoriteItem';
    CustomFavoriteItem.groupNumber=3;//have'SaveCurrentSearch'initsowngroup

    FavoriteMenu.registry.add('favorite-generator-menu',CustomFavoriteItem,0);

    returnCustomFavoriteItem;
});
