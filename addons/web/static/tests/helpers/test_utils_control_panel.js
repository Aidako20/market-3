flectra.define('web.test_utils_control_panel',function(require){
    "usestrict";

    const{click,findItem,getNode,triggerEvent}=require('web.test_utils_dom');
    const{editInput,editSelect,editAndTrigger}=require('web.test_utils_fields');

    //-------------------------------------------------------------------------
    //Exportedfunctions
    //-------------------------------------------------------------------------

    /**
     *@param{EventTarget}el
     *@param{(number|string)}menuFinder
     *@returns{Promise}
     */
    asyncfunctiontoggleMenu(el,menuFinder){
        constmenu=findItem(el,`.o_dropdown>button`,menuFinder);
        awaitclick(menu);
    }

    /**
     *@param{EventTarget}el
     *@param{(number|string)}itemFinder
     *@returns{Promise}
     */
    asyncfunctiontoggleMenuItem(el,itemFinder){
        constitem=findItem(el,`.o_menu_item>a`,itemFinder);
        awaitclick(item);
    }

    /**
     *@param{EventTarget}el
     *@param{(number|string)}itemFinder
     *@param{(number|string)}optionFinder
     *@returns{Promise}
     */
    asyncfunctiontoggleMenuItemOption(el,itemFinder,optionFinder){
        constitem=findItem(el,`.o_menu_item>a`,itemFinder);
        constoption=findItem(item.parentNode,'.o_item_option>a',optionFinder);
        awaitclick(option);
    }

    /**
     *@param{EventTarget}el
     *@param{(number|string)}itemFinder
     *@returns{boolean}
     */
    functionisItemSelected(el,itemFinder){
        constitem=findItem(el,`.o_menu_item>a`,itemFinder);
        returnitem.classList.contains('selected');
    }

    /**
     *@param{EventTarget}el
     *@param{(number|string)}itemuFinder
     *@param{(number|string)}optionFinder
     *@returns{boolean}
     */
    functionisOptionSelected(el,itemFinder,optionFinder){
        constitem=findItem(el,`.o_menu_item>a`,itemFinder);
        constoption=findItem(item.parentNode,'.o_item_option>a',optionFinder);
        returnoption.classList.contains('selected');
    }

    /**
     *@param{EventTarget}el
     *@returns{string[]}
     */
    functiongetMenuItemTexts(el){
        return[...getNode(el).querySelectorAll(`.o_dropdownul.o_menu_item`)].map(
            e=>e.innerText.trim()
        );
    }

    /**
     *@param{EventTarget}el
     *@returns{HTMLButtonElement[]}
     */
    functiongetButtons(el){
        return[...getNode(el).querySelector((`div.o_cp_bottomdiv.o_cp_buttons`)).children];
    }

    /**
     *@param{EventTarget}el
     *@returns{Promise}
     */
    asyncfunctiontoggleFilterMenu(el){
        awaitclick(getNode(el).querySelector(`.o_filter_menubutton`));
    }

    /**
     *@param{EventTarget}el
     *@returns{Promise}
     */
    asyncfunctiontoggleAddCustomFilter(el){
        awaitclick(getNode(el).querySelector(`button.o_add_custom_filter`));
    }

    /**
     *@param{EventTarget}el
     *@returns{Promise}
     */
    asyncfunctionapplyFilter(el){
        awaitclick(getNode(el).querySelector(`div.o_add_filter_menu>button.o_apply_filter`));
    }

    /**
     *@param{EventTarget}el
     *@returns{Promise}
     */
    asyncfunctiontoggleGroupByMenu(el){
        awaitclick(getNode(el).querySelector(`.o_group_by_menubutton`));
    }

    /**
     *@param{EventTarget}el
     *@returns{Promise}
     */
    asyncfunctiontoggleAddCustomGroup(el){
        awaitclick(getNode(el).querySelector(`button.o_add_custom_group_by`));
    }

    /**
     *@param{EventTarget}el
     *@param{string}fieldName
     *@returns{Promise}
     */
    asyncfunctionselectGroup(el,fieldName){
        awaiteditSelect(
            getNode(el).querySelector(`select.o_group_by_selector`),
            fieldName
        );
    }

    /**
     *@param{EventTarget}el
     *@returns{Promise}
     */
    asyncfunctionapplyGroup(el){
        awaitclick(getNode(el).querySelector(`div.o_add_group_by_menu>button.o_apply_group_by`));
    }

    /**
     *@param{EventTarget}el
     *@returns{Promise}
     */
    asyncfunctiontoggleFavoriteMenu(el){
        awaitclick(getNode(el).querySelector(`.o_favorite_menubutton`));
    }

    /**
     *@param{EventTarget}el
     *@returns{Promise}
     */
    asyncfunctiontoggleSaveFavorite(el){
        awaitclick(getNode(el).querySelector(`.o_favorite_menu.o_add_favoritebutton`));
    }

    /**
     *@param{EventTarget}el
     *@param{string}name
     *@returns{Promise}
     */
    asyncfunctioneditFavoriteName(el,name){
        awaiteditInput(getNode(el).querySelector(`.o_favorite_menu.o_add_favoriteinput[type="text"]`),name);
    }

    /**
     *@param{EventTarget}el
     *@returns{Promise}
     */
    asyncfunctionsaveFavorite(el){
        awaitclick(getNode(el).querySelector(`.o_favorite_menu.o_add_favoritebutton.o_save_favorite`));
    }

    /**
     *@param{EventTarget}el
     *@param{(string|number)}favoriteFinder
     *@returns{Promise}
     */
    asyncfunctiondeleteFavorite(el,favoriteFinder){
        constfavorite=findItem(el,`.o_favorite_menu.o_menu_item`,favoriteFinder);
        awaitclick(favorite.querySelector('i.fa-trash-o'));
    }

    /**
     *@param{EventTarget}el
     *@returns{Promise}
     */
    asyncfunctiontoggleComparisonMenu(el){
        awaitclick(getNode(el).querySelector(`div.o_comparison_menu>button`));
    }

    /**
     *@param{EventTarget}el
     *@returns{Promise}
     */
    functiongetFacetTexts(el){
        return[...getNode(el).querySelectorAll(`.o_searchview.o_searchview_facet`)].map(
            facet=>facet.innerText.trim()
        );
    }

    /**
     *@param{EventTarget}el
     *@param{(string|number)}facetFinder
     *@returns{Promise}
     */
    asyncfunctionremoveFacet(el,facetFinder=0){
        constfacet=findItem(el,`.o_searchview.o_searchview_facet`,facetFinder);
        awaitclick(facet.querySelector('.o_facet_remove'));
    }

    /**
     *@param{EventTarget}el
     *@param{string}value
     *@returns{Promise}
     */
    asyncfunctioneditSearch(el,value){
        awaiteditInput(getNode(el).querySelector(`.o_searchview_input`),value);
    }

    /**
     *@param{EventTarget}el
     *@returns{Promise}
     */
    asyncfunctionvalidateSearch(el){
        awaittriggerEvent(
            getNode(el).querySelector(`.o_searchview_input`),
            'keydown',{key:'Enter'}
        );
    }

    /**
     *@param{EventTarget}el
     *@param{string}[menuFinder="Action"]
     *@returns{Promise}
     */
    asyncfunctiontoggleActionMenu(el,menuFinder="Action"){
        constdropdown=findItem(el,`.o_cp_action_menusbutton`,menuFinder);
        awaitclick(dropdown);
    }

    /**
     *@param{EventTarget}el
     *@returns{Promise}
     */
    asyncfunctionpagerPrevious(el){
        awaitclick(getNode(el).querySelector(`.o_pagerbutton.o_pager_previous`));
    }

    /**
     *@param{EventTarget}el
     *@returns{Promise}
     */
    asyncfunctionpagerNext(el){
        awaitclick(getNode(el).querySelector(`.o_pagerbutton.o_pager_next`));
    }

    /**
     *@param{EventTarget}el
     *@returns{string}
     */
    functiongetPagerValue(el){
        constpagerValue=getNode(el).querySelector(`.o_pager_counter.o_pager_value`);
        switch(pagerValue.tagName){
            case'INPUT':
                returnpagerValue.value;
            case'SPAN':
                returnpagerValue.innerText.trim();
        }
    }

    /**
     *@param{EventTarget}el
     *@returns{string}
     */
    functiongetPagerSize(el){
        returngetNode(el).querySelector(`.o_pager_counterspan.o_pager_limit`).innerText.trim();
    }

    /**
     *@param{EventTarget}el
     *@param{string}value
     *@returns{Promise}
     */
    asyncfunctionsetPagerValue(el,value){
        letpagerValue=getNode(el).querySelector(`.o_pager_counter.o_pager_value`);
        if(pagerValue.tagName==='SPAN'){
            awaitclick(pagerValue);
        }
        pagerValue=getNode(el).querySelector(`.o_pager_counterinput.o_pager_value`);
        if(!pagerValue){
            thrownewError("Pagervalueisbeingeditedandcannotbechanged.");
        }
        awaiteditAndTrigger(pagerValue,value,['change','blur']);
    }

    /**
     *@param{EventTarget}el
     *@param{string}viewType
     *@returns{Promise}
     */
    asyncfunctionswitchView(el,viewType){
        awaitclick(getNode(el).querySelector(`button.o_switch_view.o_${viewType}`));
    }

    return{
        //Genericinteractions
        toggleMenu,
        toggleMenuItem,
        toggleMenuItemOption,
        isItemSelected,
        isOptionSelected,
        getMenuItemTexts,
        //Buttoninteractions
        getButtons,
        //FilterMenuinteractions
        toggleFilterMenu,
        toggleAddCustomFilter,
        applyFilter,
        //GroupByMenuinteractions
        toggleGroupByMenu,
        toggleAddCustomGroup,
        selectGroup,
        applyGroup,
        //FavoriteMenuinteractions
        toggleFavoriteMenu,
        toggleSaveFavorite,
        editFavoriteName,
        saveFavorite,
        deleteFavorite,
        //ComparisonMenuinteractions
        toggleComparisonMenu,
        //SearchBarinteractions
        getFacetTexts,
        removeFacet,
        editSearch,
        validateSearch,
        //Actionmenusinteractions
        toggleActionMenu,
        //Pagerinteractions
        pagerPrevious,
        pagerNext,
        getPagerValue,
        getPagerSize,
        setPagerValue,
        //Viewswitcher
        switchView,
    };
});
