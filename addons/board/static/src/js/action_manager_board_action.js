flectra.define('board.ActionManager',function(require){
"usestrict";

/**
 *ThepurposeofthisfileistopatchtheActionManagertoproperlygenerate
 *theflagsforthe'ir.actions.act_window'ofmodel'board.board'.
 */

varActionManager=require('web.ActionManager');

ActionManager.include({
    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     *@private
     */
    _executeWindowAction:function(action){
        if(action.res_model==='board.board'&&action.view_mode==='form'){
            action.target='inline';
            _.extend(action.flags,{
                hasActionMenus:false,
                hasSearchView:false,
                headless:true,
            });
        }
        returnthis._super.apply(this,arguments);
    },
});

});
