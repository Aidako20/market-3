flectra.define('point_of_sale.OrderManagementControlPanel',function(require){
    'usestrict';

    const{useContext}=owl.hooks;
    const{useAutofocus,useListener}=require('web.custom_hooks');
    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');
    constOrderFetcher=require('point_of_sale.OrderFetcher');
    constcontexts=require('point_of_sale.PosContext');

    //NOTE:Theseareconstantssothattheyareonlyinstantiatedonce
    //andtheycanbeusedefficientlybytheOrderManagementControlPanel.
    constVALID_SEARCH_TAGS=newSet(['date','customer','client','name','order']);
    constFIELD_MAP={
        date:'date_order',
        customer:'partner_id.display_name',
        client:'partner_id.display_name',
        name:'pos_reference',
        order:'pos_reference',
    };
    constSEARCH_FIELDS=['pos_reference','partner_id.display_name','date_order'];

    functiongetDomainForSingleCondition(fields,toSearch){
        constorSymbols=Array(fields.length-1).fill('|');
        returnorSymbols.concat(fields.map((field)=>[field,'ilike',`%${toSearch}%`]));
    }

    /**
     *@emitsclose-screen
     *@emitsprev-page
     *@emitsnext-page
     *@emitssearch
     */
    classOrderManagementControlPanelextendsPosComponent{
        constructor(){
            super(...arguments);
            //Weareusingcontextbecausewewantthe`searchString`tobealive
            //evenifthiscomponentisdestroyed(unmounted).
            this.orderManagementContext=useContext(contexts.orderManagement);
            useListener('clear-search',this._onClearSearch);
            useAutofocus({selector:'input'});
        }
        onInputKeydown(event){
            if(event.key==='Enter'){
                this.trigger('search',this._computeDomain());
            }
        }
        getshowPageControls(){
            returnOrderFetcher.lastPage>1;
        }
        getpageNumber(){
            constcurrentPage=OrderFetcher.currentPage;
            constlastPage=OrderFetcher.lastPage;
            returnisNaN(lastPage)?'':`(${currentPage}/${lastPage})`;
        }
        getvalidSearchTags(){
            returnVALID_SEARCH_TAGS;
        }
        getfieldMap(){
            returnFIELD_MAP;
        }
        getsearchFields(){
            returnSEARCH_FIELDS;
        }
        /**
         *E.g.1
         *```
         *  searchString='Customer1'
         *  result=[
         *     '|',
         *     '|',
         *     ['pos_reference','ilike','%Customer1%'],
         *     ['partner_id.display_name','ilike','%Customer1%'],
         *     ['date_order','ilike','%Customer1%']
         *  ]
         *```
         *
         *E.g.2
         *```
         *  searchString='date:2020-05'
         *  result=[
         *     ['date_order','ilike','%2020-05%']
         *  ]
         *```
         *
         *E.g.3
         *```
         *  searchString='customer:Steward,date:2020-05-01'
         *  result=[
         *     ['partner_id.display_name','ilike','%Steward%'],
         *     ['date_order','ilike','%2020-05-01%']
         *  ]
         *```
         */
        _computeDomain(){
            constinput=this.orderManagementContext.searchString.trim();
            if(!input)return;

            constsearchConditions=this.orderManagementContext.searchString.split(/[,&]\s*/);
            if(searchConditions.length===1){
                letcond=searchConditions[0].split(/:\s*/);
                if(cond.length===1){
                    returngetDomainForSingleCondition(this.searchFields,cond[0]);
                }
            }
            constdomain=[];
            for(letcondofsearchConditions){
                let[tag,value]=cond.split(/:\s*/);
                if(!this.validSearchTags.has(tag))continue;
                domain.push([this.fieldMap[tag],'ilike',`%${value}%`]);
            }
            returndomain;
        }
        _onClearSearch(){
            this.orderManagementContext.searchString='';
            this.onInputKeydown({key:'Enter'});
        }
    }
    OrderManagementControlPanel.template='OrderManagementControlPanel';

    Registries.Component.add(OrderManagementControlPanel);

    returnOrderManagementControlPanel;
});
