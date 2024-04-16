flectra.define('board.AddToGoogleSpreadsheetMenu',function(require){
    "usestrict";

    constDomain=require('web.Domain');
    constDropdownMenuItem=require('web.DropdownMenuItem');
    constFavoriteMenu=require('web.FavoriteMenu');

    constDialog=require('web.OwlDialog');
    const{useState}=owl.hooks;

    /**
     *'AddtoGooglespreadsheet'menu
     *
     *Componentconsistingonlyofabuttoncallingtheservertoaddthecurrent
     *viewtotheuser'sspreadsheetconfiguration.
     *Thiscomponentisonlyavailableinactionsoftype'ir.actions.act_window'.
     *@extendsDropdownMenuItem
     */
    classAddToGoogleSpreadsheetMenuextendsDropdownMenuItem{
        constructor(){
            super(...arguments);

            this.state=useState({
                showDialog:false,
                url:false,
                formula:false,
            });
        }

        //---------------------------------------------------------------------
        //Handlers
        //---------------------------------------------------------------------

        /**
         *@private
         */
        async_onAddToSpreadsheet(){
            constsearchQuery=this.env.searchModel.get('query');
            constlistView=this.env.action.views.find(view=>view.type==='list');
            constmodelName=this.env.action.res_model;
            constdomain=Domain.prototype.arrayToString(searchQuery.domain);
            constgroupBys=searchQuery.groupBy.join("");
            constlistViewId=listView?listView.viewID:false;
            constresult=awaitthis.rpc({
                model:'google.drive.config',
                method:'set_spreadsheet',
                args:[modelName,domain,groupBys,listViewId],
            });
            if(result.deprecated){
                this.state.url=result.url;
                this.state.formula=result.formula;
                this.state.showDialog=true;
                this.state.open=false;
                return;
            }
            if(result.url){
                //AccordingtoMDNdoc,oneshouldnotuse_blankastitle.
                //todo:findagoodnameforthenewwindow
                window.open(result.url,'_blank');
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
            returnenv.action.type==='ir.actions.act_window';
        }
    }

    AddToGoogleSpreadsheetMenu.components={Dialog};
    AddToGoogleSpreadsheetMenu.props={};
    AddToGoogleSpreadsheetMenu.template='AddToGoogleSpreadsheetMenu';

    FavoriteMenu.registry.add('add-to-google-spreadsheet-menu',AddToGoogleSpreadsheetMenu,20);

    returnAddToGoogleSpreadsheetMenu;
});
