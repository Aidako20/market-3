flectra.define('base_import.ImportMenu',function(require){
    "usestrict";

    constDropdownMenuItem=require('web.DropdownMenuItem');
    constFavoriteMenu=require('web.FavoriteMenu');
    const{useModel}=require('web/static/src/js/model.js');

    /**
     *ImportRecordsmenu
     *
     *Thiscomponentisusedtoimporttherecordsforparticularmodel.
     *
     *@extendsDropdownMenuItem
     */
    classImportMenuextendsDropdownMenuItem{
        constructor(){
            super(...arguments);
            this.model=useModel('searchModel');
        }

        //---------------------------------------------------------------------
        //Handlers
        //---------------------------------------------------------------------

        /**
         *@private
         */
        _onImportClick(){
            constaction={
                type:'ir.actions.client',
                tag:'import',
                params:{
                    model:this.model.config.modelName,
                    context:this.model.config.context,
                }
            };
            this.trigger('do-action',{action:action});
        }

        //---------------------------------------------------------------------
        //Static
        //---------------------------------------------------------------------

        /**
         *@param{Object}env
         *@returns{boolean}
         */
        staticshouldBeDisplayed(env){
            returnenv.view&&
                ['kanban','list'].includes(env.view.type)&&
                !env.device.isMobile&&
                !!JSON.parse(env.view.arch.attrs.import||'1')&&
                !!JSON.parse(env.view.arch.attrs.create||'1');
        }
    }

    ImportMenu.props={};
    ImportMenu.template='base_import.ImportMenu';

    FavoriteMenu.registry.add('import-menu',ImportMenu,1);

    returnImportMenu;
});
