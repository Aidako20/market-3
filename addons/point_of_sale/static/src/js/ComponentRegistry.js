flectra.define('point_of_sale.ComponentRegistry',function(require){
    'usestrict';

    constPosComponent=require('point_of_sale.PosComponent');
    constClassRegistry=require('point_of_sale.ClassRegistry');

    classComponentRegistryextendsClassRegistry{
        freeze(){
            super.freeze();
            //MakesurePosComponenthasthecompiledclasses.
            //Thisway,wedon'tneedtoexplicitlydeclarethat
            //asetofcomponentsischildrenofanother.
            PosComponent.components={};
            for(let[base,compiledClass]ofthis.cache.entries()){
                PosComponent.components[base.name]=compiledClass;
            }
        }
        _recompute(base,old){
            constres=super._recompute(base,old);
            if(typeofbase==='string'){
                base=this.baseNameMap[base];
            }
            PosComponent.components[base.name]=res;
            returnres;
        }
    }

    returnComponentRegistry;
});
