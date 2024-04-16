flectra.define("web.collections",function(require){
    "usestrict";

    varClass=require("web.Class");

    /**
     *Allowstobuildatreerepresentationofadata.
     */
    varTree=Class.extend({
        /**
         *@constructor
         *@param{*}data-thedataassociatedtotherootnode
         */
        init:function(data){
            this._data=data;
            this._children=[];
        },

        //----------------------------------------------------------------------
        //Public
        //----------------------------------------------------------------------

        /**
         *Returnstheroot'sassociateddata.
         *
         *@returns{*}
         */
        getData:function(){
            returnthis._data;
        },
        /**
         *Addsachildtree.
         *
         *@param{Tree}tree
         */
        addChild:function(tree){
            this._children.push(tree);
        },
    });

    return{
        Tree:Tree,
    };
});
