flectra.define('account.ShowResequenceRenderer',function(require){
"usestrict";

const{Component}=owl;
const{useState}=owl.hooks;
constAbstractFieldOwl=require('web.AbstractFieldOwl');
constfield_registry=require('web.field_registry_owl');

classChangeLineextendsComponent{}
ChangeLine.template='account.ResequenceChangeLine';
ChangeLine.props=["changeLine",'ordering'];


classShowResequenceRendererextendsAbstractFieldOwl{
    constructor(...args){
        super(...args);
        this.data=this.value?JSON.parse(this.value):{
            changeLines:[],
            ordering:'date',
        };
    }
    asyncwillUpdateProps(nextProps){
        awaitsuper.willUpdateProps(nextProps);
        Object.assign(this.data,JSON.parse(this.value));
    }
}
ShowResequenceRenderer.template='account.ResequenceRenderer';
ShowResequenceRenderer.components={ChangeLine}

field_registry.add('account_resequence_widget',ShowResequenceRenderer);
returnShowResequenceRenderer;
});
